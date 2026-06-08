"""Gemini API provider with key rotation."""

import logging
import asyncio
from typing import Optional, List
import aiohttp

import google.generativeai as genai
from google.api_core.exceptions import (
    ResourceExhausted,
    TooManyRequests,
    ServiceUnavailable,
)

from config.settings import settings
from database.queries import APIKeyQueries

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Gemini API provider with key rotation and error handling."""

    def __init__(self) -> None:
        """Initialize provider."""
        self.api_keys = settings.get_gemini_keys()
        self.current_key_index = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self) -> None:
        """Initialize session."""
        connector = None
        
        if settings.use_vpn and settings.vpn_proxy_url:
            connector = aiohttp.TCPConnector(ssl=False)
            
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=settings.gemini_request_timeout),
        )

    async def close(self) -> None:
        """Close session."""
        if self.session:
            await self.session.close()

    def _get_current_key(self) -> str:
        """Get current API key."""
        return self.api_keys[self.current_key_index]

    def _rotate_key(self) -> str:
        """Rotate to next API key."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        key = self._get_current_key()
        logger.info(
            f"Rotated API key. New index: {self.current_key_index}/{len(self.api_keys)}"
        )
        return key

    async def generate_response(
        self,
        messages: List[dict],
        persona: str = "You are a helpful AI assistant.",
    ) -> Optional[str]:
        """Generate response from Gemini API with retry and key rotation."""
        max_retries = len(self.api_keys)
        retry_count = 0

        while retry_count < max_retries:
            try:
                api_key = self._get_current_key()
                genai.configure(api_key=api_key)

                # Prepare message history
                chat_messages = []
                for msg in messages:
                    if msg["role"] == "user":
                        chat_messages.append({"role": "user", "parts": [msg["content"]]})
                    else:
                        chat_messages.append(
                            {"role": "model", "parts": [msg["content"]]}
                        )

                # Add persona as system instruction
                model = genai.GenerativeModel(
                    model_name=settings.gemini_model,
                    system_instruction=persona,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.gemini_temperature,
                        max_output_tokens=settings.gemini_max_output_tokens,
                    ),
                )

                # Start chat session
                chat = model.start_chat(history=chat_messages)

                # Generate response
                response = await asyncio.to_thread(
                    chat.send_message,
                    messages[-1]["content"] if messages else "Hello",
                )

                # Record successful request
                await APIKeyQueries.record_request(api_key)
                logger.info(
                    f"Successfully generated response using key index {self.current_key_index}"
                )

                return response.text

            except ResourceExhausted:
                logger.warning(
                    f"API quota exceeded for key index {self.current_key_index}"
                )
                await APIKeyQueries.record_error(api_key)
                self._rotate_key()
                retry_count += 1

            except TooManyRequests:
                logger.warning(
                    f"Rate limited on key index {self.current_key_index}"
                )
                await APIKeyQueries.record_error(api_key)
                self._rotate_key()
                retry_count += 1
                await asyncio.sleep(2)

            except ServiceUnavailable:
                logger.warning(
                    f"Service unavailable for key index {self.current_key_index}"
                )
                await APIKeyQueries.record_error(api_key)
                self._rotate_key()
                retry_count += 1
                await asyncio.sleep(1)

            except asyncio.TimeoutError:
                logger.warning(
                    f"Timeout for key index {self.current_key_index}"
                )
                await APIKeyQueries.record_error(api_key)
                self._rotate_key()
                retry_count += 1

            except Exception as e:
                logger.error(f"Unexpected error with key index {self.current_key_index}: {str(e)}")
                await APIKeyQueries.record_error(api_key)
                self._rotate_key()
                retry_count += 1

        logger.error("All API keys exhausted")
        return None


# Global provider instance
gemini_provider = GeminiProvider()
