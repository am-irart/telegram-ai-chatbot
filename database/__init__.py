"""Database package initialization."""

from database.db import db, Database
from database.queries import (
    UserQueries,
    MessageQueries,
    ChatQueries,
    StatisticsQueries,
    APIKeyQueries,
    RateLimitQueries,
)

__all__ = [
    "db",
    "Database",
    "UserQueries",
    "MessageQueries",
    "ChatQueries",
    "StatisticsQueries",
    "APIKeyQueries",
    "RateLimitQueries",
]
