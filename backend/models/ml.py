from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CHAR, DECIMAL, JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base
from models.types import UBigInt, UInt, USmallInt, enum

ML_RUN_STATUSES = ("running", "succeeded", "failed")
SUBJECT_TYPES = ("listing", "user")
RECOMMENDATION_KINDS = ("similar", "also_stayed", "for_you", "cross_city")


class ListingEmbedding(Base):
    __tablename__ = "listing_embeddings"

    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_listing_embeddings_listing", ondelete="CASCADE"),
        primary_key=True,
    )
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    dim: Mapped[int] = mapped_column(USmallInt, nullable=False)
    vector: Mapped[bytes] = mapped_column(mysql.MEDIUMBLOB, nullable=False)
    text_hash: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class MlRun(Base):
    __tablename__ = "ml_runs"
    __table_args__ = (Index("idx_ml_runs_status_finished", "status", "finished_at"),)

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(enum(*ML_RUN_STATUSES), nullable=False, server_default="running")
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    git_sha: Mapped[str | None] = mapped_column(CHAR(40))
    notes: Mapped[str | None] = mapped_column(String(500))


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        UniqueConstraint(
            "run_id", "subject_type", "subject_id", "kind", "position",
            name="uq_recommendations_slot",
        ),
        Index("idx_recommendations_lookup", "subject_type", "subject_id", "kind", "run_id"),
        Index("idx_recommendations_listing", "listing_id"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("ml_runs.id", name="fk_recommendations_run", ondelete="CASCADE"),
        nullable=False,
    )
    subject_type: Mapped[str] = mapped_column(enum(*SUBJECT_TYPES), nullable=False)
    subject_id: Mapped[int] = mapped_column(UBigInt, nullable=False)
    kind: Mapped[str] = mapped_column(enum(*RECOMMENDATION_KINDS), nullable=False)
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_recommendations_listing", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(USmallInt, nullable=False)
    score: Mapped[Decimal] = mapped_column(DECIMAL(8, 5), nullable=False)
    reason: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class ListingReviewInsight(Base):
    __tablename__ = "listing_review_insights"

    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_listing_review_insights_listing", ondelete="CASCADE"),
        primary_key=True,
    )
    loves: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    watch_outs: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    review_count_used: Mapped[int] = mapped_column(UInt, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
