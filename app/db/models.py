
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):

    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Unique user identifier"
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User's email address (unique)"
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password"
    )
    
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
        doc="User role (user, admin, etc.)"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when user was created"
    )
    
    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="User's chat messages"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class ChatMessage(Base):
    
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        doc="Unique message identifier"
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to user who owns this message"
    )
    
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Message role (user, assistant, system)"
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Message content text"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Timestamp when message was created"
    )
    

    user: Mapped["User"] = relationship(
        "User",
        back_populates="messages",
        lazy="select",
        doc="User who sent this message"
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, user_id={self.user_id}, role={self.role}, created_at={self.created_at})>"
