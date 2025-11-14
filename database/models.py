from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    quests: Mapped[list["Quest"]] = relationship(back_populates="user")
    chat_history: Mapped[list["ChatHistory"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.telegram_id} - {self.first_name}>"

class Quest(Base):
    """Модель квеста."""
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tasks: Mapped[str] = mapped_column(Text, nullable=False)
    completed_tasks: Mapped[str] = mapped_column(Text, default=[""])
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    quest_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Связи
    user: Mapped["User"] = relationship(back_populates="quests")

    def __repr__(self):
        return f"<Quest {self.id} - {self.title} ({self.status})>"


class ChatHistory(Base):
    """Модель истории чата."""
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_from_user: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связи
    user: Mapped["User"] = relationship(back_populates="chat_history")

    def __repr__(self):
        sender = "User" if self.is_from_user else "Bot"
        return f"<ChatHistory {self.id} - {sender}>"
