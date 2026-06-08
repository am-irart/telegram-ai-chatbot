"""Database models and data structures."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User data model."""

    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    persona: str = "You are a helpful AI assistant."
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamps."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Message:
    """Message data model."""

    message_id: int
    user_id: int
    chat_id: int
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Chat:
    """Chat session data model."""

    chat_id: int
    user_id: int
    chat_type: str  # "private", "group", "supergroup"
    title: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Statistics:
    """Statistics data model."""

    stat_id: int
    total_users: int = 0
    total_chats: int = 0
    total_messages: int = 0
    total_ai_requests: int = 0
    total_active_users: int = 0
    last_updated: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


@dataclass
class APIKeyStats:
    """API key statistics data model."""

    key_id: int
    key_hash: str
    total_requests: int = 0
    total_errors: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
