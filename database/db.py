"""Database initialization and schema creation."""

import sqlite3
from pathlib import Path
import logging
from typing import Optional
import aiosqlite

from config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = settings.database_path) -> None:
        """Initialize database."""
        self.db_path = Path(db_path)
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to database."""
        self.connection = await aiosqlite.connect(str(self.db_path))
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()
        logger.info(f"Connected to database: {self.db_path}")

    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def create_tables(self) -> None:
        """Create all required tables."""
        if not self.connection:
            return

        cursor = await self.connection.cursor()

        # Users table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                persona TEXT DEFAULT 'You are a helpful AI assistant.',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Chats table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                chat_type TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
        )

        # Messages table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
            """
        )

        # Statistics table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS statistics (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_users INTEGER DEFAULT 0,
                total_chats INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                total_ai_requests INTEGER DEFAULT 0,
                total_active_users INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # API Key stats table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_key_stats (
                key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                total_requests INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Rate limit table
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rate_limits (
                limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                request_count INTEGER DEFAULT 0,
                reset_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
        )

        # Initialize statistics if empty
        await cursor.execute("SELECT COUNT(*) FROM statistics")
        count = await cursor.fetchone()
        if count[0] == 0:
            await cursor.execute(
                "INSERT INTO statistics (stat_id) VALUES (1)"
            )

        await self.connection.commit()
        logger.info("Database tables created successfully")

    async def execute(
        self, query: str, params: tuple = ()
    ) -> Optional[aiosqlite.Cursor]:
        """Execute a query."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = await self.connection.cursor()
        await cursor.execute(query, params)
        return cursor

    async def execute_many(self, query: str, params: list) -> None:
        """Execute multiple queries."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = await self.connection.cursor()
        await cursor.executemany(query, params)
        await self.connection.commit()

    async def commit(self) -> None:
        """Commit changes."""
        if self.connection:
            await self.connection.commit()

    async def rollback(self) -> None:
        """Rollback changes."""
        if self.connection:
            await self.connection.rollback()


# Global database instance
db = Database()
