"""Rate limiting middleware."""

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from config.settings import settings
from config.constants import RATE_LIMIT_MESSAGE
from database.queries import RateLimitQueries

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware to enforce rate limiting."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """Process middleware."""
        if not event.message or not event.message.from_user:
            return await handler(event, data)

        user_id = event.message.from_user.id
        message: Message = event.message

        # Check rate limit
        current_count = await RateLimitQueries.get_request_count(user_id)

        if current_count >= settings.rate_limit_requests:
            logger.warning(
                f"Rate limit exceeded for user {user_id}: {current_count}/{settings.rate_limit_requests}"
            )
            await message.answer(RATE_LIMIT_MESSAGE)
            return

        # Increment count
        await RateLimitQueries.increment_request_count(
            user_id, settings.rate_limit_period_hours
        )

        return await handler(event, data)
