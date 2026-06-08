"""Database query operations."""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from database.db import db
from database.models import User, Message, Chat, Statistics, APIKeyStats

logger = logging.getLogger(__name__)


class UserQueries:
    """User-related database queries."""

    @staticmethod
    async def get_or_create(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Get or create a user."""
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            return User(
                user_id=row["user_id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                persona=row["persona"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )

        # Create new user
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, username, first_name, last_name),
        )
        await db.commit()

        return User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

    @staticmethod
    async def update_persona(user_id: int, persona: str) -> None:
        """Update user persona."""
        await db.execute(
            """
            UPDATE users SET persona = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (persona, user_id),
        )
        await db.commit()

    @staticmethod
    async def get_persona(user_id: int) -> str:
        """Get user persona."""
        cursor = await db.execute(
            "SELECT persona FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row["persona"] if row else "You are a helpful AI assistant."

    @staticmethod
    async def count_users() -> int:
        """Count total users."""
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0


class MessageQueries:
    """Message-related database queries."""

    @staticmethod
    async def add_message(
        user_id: int, chat_id: int, role: str, content: str
    ) -> int:
        """Add a message to the database."""
        cursor = await db.execute(
            """
            INSERT INTO messages (user_id, chat_id, role, content)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, chat_id, role, content),
        )
        await db.commit()
        return cursor.lastrowid

    @staticmethod
    async def get_history(
        user_id: int, chat_id: int, limit: int = 10
    ) -> List[dict]:
        """Get conversation history for a user."""
        cursor = await db.execute(
            """
            SELECT role, content, created_at FROM messages
            WHERE user_id = ? AND chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, chat_id, limit),
        )
        rows = await cursor.fetchall()
        return [
            {"role": row["role"], "content": row["content"]}
            for row in reversed(rows)
        ]

    @staticmethod
    async def clear_history(user_id: int) -> None:
        """Clear conversation history for a user."""
        await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await db.commit()

    @staticmethod
    async def count_messages() -> int:
        """Count total messages."""
        cursor = await db.execute("SELECT COUNT(*) FROM messages")
        row = await cursor.fetchone()
        return row[0] if row else 0


class ChatQueries:
    """Chat-related database queries."""

    @staticmethod
    async def get_or_create(
        chat_id: int,
        user_id: int,
        chat_type: str,
        title: Optional[str] = None,
    ) -> Chat:
        """Get or create a chat."""
        cursor = await db.execute(
            "SELECT * FROM chats WHERE chat_id = ?", (chat_id,)
        )
        row = await cursor.fetchone()

        if row:
            return Chat(
                chat_id=row["chat_id"],
                user_id=row["user_id"],
                chat_type=row["chat_type"],
                title=row["title"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

        await db.execute(
            """
            INSERT INTO chats (chat_id, user_id, chat_type, title)
            VALUES (?, ?, ?, ?)
            """,
            (chat_id, user_id, chat_type, title),
        )
        await db.commit()

        return Chat(chat_id=chat_id, user_id=user_id, chat_type=chat_type, title=title)

    @staticmethod
    async def count_chats() -> int:
        """Count total chats."""
        cursor = await db.execute("SELECT COUNT(*) FROM chats")
        row = await cursor.fetchone()
        return row[0] if row else 0


class StatisticsQueries:
    """Statistics-related database queries."""

    @staticmethod
    async def get_stats() -> dict:
        """Get current statistics."""
        cursor = await db.execute("SELECT * FROM statistics WHERE stat_id = 1")
        row = await cursor.fetchone()
        if not row:
            return {
                "total_users": 0,
                "total_chats": 0,
                "total_messages": 0,
                "total_ai_requests": 0,
                "total_active_users": 0,
            }
        return {
            "total_users": row["total_users"],
            "total_chats": row["total_chats"],
            "total_messages": row["total_messages"],
            "total_ai_requests": row["total_ai_requests"],
            "total_active_users": row["total_active_users"],
        }

    @staticmethod
    async def update_stats() -> None:
        """Update statistics from database."""
        total_users = await UserQueries.count_users()
        total_chats = await ChatQueries.count_chats()
        total_messages = await MessageQueries.count_messages()

        cursor = await db.execute(
            """
            SELECT COUNT(DISTINCT user_id) FROM messages
            WHERE created_at > datetime('now', '-1 day')
            """
        )
        active_users = await cursor.fetchone()
        active_users = active_users[0] if active_users else 0

        await db.execute(
            """
            UPDATE statistics SET
                total_users = ?,
                total_chats = ?,
                total_messages = ?,
                total_active_users = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE stat_id = 1
            """,
            (total_users, total_chats, total_messages, active_users),
        )
        await db.commit()

    @staticmethod
    async def increment_ai_requests() -> None:
        """Increment total AI requests."""
        await db.execute(
            """
            UPDATE statistics SET
                total_ai_requests = total_ai_requests + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE stat_id = 1
            """
        )
        await db.commit()


class APIKeyQueries:
    """API key statistics queries."""

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    async def record_request(api_key: str) -> None:
        """Record an API request."""
        key_hash = APIKeyQueries._hash_key(api_key)
        
        cursor = await db.execute(
            "SELECT key_id FROM api_key_stats WHERE key_hash = ?", (key_hash,)
        )
        row = await cursor.fetchone()

        if row:
            await db.execute(
                """
                UPDATE api_key_stats SET
                    total_requests = total_requests + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE key_hash = ?
                """,
                (key_hash,),
            )
        else:
            await db.execute(
                """
                INSERT INTO api_key_stats (key_hash, total_requests, last_used)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                """,
                (key_hash,),
            )

        await db.commit()

    @staticmethod
    async def record_error(api_key: str) -> None:
        """Record an API error."""
        key_hash = APIKeyQueries._hash_key(api_key)

        cursor = await db.execute(
            "SELECT key_id FROM api_key_stats WHERE key_hash = ?", (key_hash,)
        )
        row = await cursor.fetchone()

        if row:
            await db.execute(
                """
                UPDATE api_key_stats SET total_errors = total_errors + 1
                WHERE key_hash = ?
                """,
                (key_hash,),
            )
        else:
            await db.execute(
                """
                INSERT INTO api_key_stats (key_hash, total_errors)
                VALUES (?, 1)
                """,
                (key_hash,),
            )

        await db.commit()

    @staticmethod
    async def get_key_stats() -> List[dict]:
        """Get statistics for all API keys."""
        cursor = await db.execute(
            """
            SELECT key_hash, total_requests, total_errors, last_used
            FROM api_key_stats
            ORDER BY total_requests DESC
            """
        )
        rows = await cursor.fetchall()
        return [
            {
                "key_hash": row["key_hash"][:8] + "...",
                "total_requests": row["total_requests"],
                "total_errors": row["total_errors"],
                "last_used": row["last_used"],
            }
            for row in rows
        ]


class RateLimitQueries:
    """Rate limit queries."""

    @staticmethod
    async def get_request_count(user_id: int) -> int:
        """Get current request count for user."""
        cursor = await db.execute(
            "SELECT request_count FROM rate_limits WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            # Check if reset time has passed
            cursor = await db.execute(
                "SELECT reset_at FROM rate_limits WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            if row and row["reset_at"]:
                reset_at = datetime.fromisoformat(row["reset_at"])
                if datetime.utcnow() > reset_at:
                    await RateLimitQueries.reset_count(user_id)
                    return 0
            return row["request_count"] if row else 0

        return 0

    @staticmethod
    async def increment_request_count(user_id: int, period_hours: int = 1) -> None:
        """Increment request count for user."""
        cursor = await db.execute(
            "SELECT user_id FROM rate_limits WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        reset_time = datetime.utcnow() + timedelta(hours=period_hours)

        if row:
            await db.execute(
                """
                UPDATE rate_limits SET
                    request_count = request_count + 1,
                    reset_at = ?
                WHERE user_id = ?
                """,
                (reset_time.isoformat(), user_id),
            )
        else:
            await db.execute(
                """
                INSERT INTO rate_limits (user_id, request_count, reset_at)
                VALUES (?, 1, ?)
                """,
                (user_id, reset_time.isoformat()),
            )

        await db.commit()

    @staticmethod
    async def reset_count(user_id: int) -> None:
        """Reset request count for user."""
        await db.execute(
            """
            UPDATE rate_limits SET request_count = 0
            WHERE user_id = ?
            """,
            (user_id,),
        )
        await db.commit()
