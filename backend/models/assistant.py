from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import CHAR, JSON, Date, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base
from models.types import UBigInt, UInt, enum

CHAT_ROLES = ("user", "assistant", "tool")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("idx_chat_sessions_user", "user_id"),
        Index("idx_chat_sessions_last_active", "last_active_at"),
    )

    id: Mapped[str] = mapped_column(CHAR(26), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("users.id", name="fk_chat_sessions_user", ondelete="CASCADE")
    )
    anon_key_hash: Mapped[str | None] = mapped_column(CHAR(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (Index("idx_chat_messages_session", "session_id", "id"),)

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        CHAR(26),
        ForeignKey("chat_sessions.id", name="fk_chat_messages_session", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(enum(*CHAT_ROLES), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_name: Mapped[str | None] = mapped_column(String(60))
    tool_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    cited_listing_ids: Mapped[list[int] | None] = mapped_column(JSON)
    tokens_in: Mapped[int | None] = mapped_column(UInt)
    tokens_out: Mapped[int | None] = mapped_column(UInt)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class AiUsageDaily(Base):
    __tablename__ = "ai_usage_daily"

    subject_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    requests: Mapped[int] = mapped_column(UInt, nullable=False, server_default=text("'0'"))
