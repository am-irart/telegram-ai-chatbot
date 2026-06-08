"""Authentication middleware for whitelist checking."""

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from config.settings import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware to check if user/group is whitelisted."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        """Process middleware."""
        if not settings.whitelist_enabled:
            return await handler(event, data)

        # Get user and chat from event
        message = None
        user_id = None
        chat_id = None

        if event.message:
            message = event.message
            user_id = message.from_user.id if message.from_user else None
            chat_id = message.chat.id

        elif event.callback_query:
            callback_query = event.callback_query
            user_id = callback_query.from_user.id
            chat_id = callback_query.message.chat.id if callback_query.message else None

        if not user_id:
            return

        # Check whitelist
        whitelist_users = settings.get_whitelist_users()
        whitelist_groups = settings.get_whitelist_groups()

        # Check if user is allowed
        if chat_id and chat_id < 0:  # Group chat
            if whitelist_groups and chat_id not in whitelist_groups:
                logger.warning(
                    f"Unauthorized group access attempt: group_id={chat_id}, user_id={user_id}"
                )
                if message:
                    await message.answer("❌ This group is not authorized to use this bot.")
                return
        else:  # Private chat
            if whitelist_users and user_id not in whitelist_users:
                logger.warning(
                    f"Unauthorized user access attempt: user_id={user_id}"
                )
                if message:
                    await message.answer("❌ You are not authorized to use this bot.")
                return

        return await handler(event, data)
