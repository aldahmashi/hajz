from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base
from models.types import UBigInt, UTinyInt, enum

REVIEW_SOURCES = ("imported", "app")
INTERACTION_TYPES = ("view", "save", "book", "review", "imported_stay")

# BR-REC-01
INTERACTION_WEIGHTS = {
    "view": Decimal("1"),
    "save": Decimal("3"),
    "book": Decimal("5"),
    "review": Decimal("5"),
    "imported_stay": Decimal("5"),
}


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (Index("idx_wishlist_items_listing", "listing_id"),)

    user_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("users.id", name="fk_wishlist_items_user", ondelete="CASCADE"),
        primary_key=True,
    )
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_wishlist_items_listing", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("booking_id", name="uq_reviews_booking"),
        UniqueConstraint("source_review_id", name="uq_reviews_source"),
        Index("idx_reviews_listing_created", "listing_id", "created_at"),
        Index("idx_reviews_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_reviews_listing", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(enum(*REVIEW_SOURCES), nullable=False)
    source_review_id: Mapped[int | None] = mapped_column(UBigInt)
    booking_id: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("bookings.id", name="fk_reviews_booking", ondelete="SET NULL")
    )
    user_id: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("users.id", name="fk_reviews_user", ondelete="SET NULL")
    )
    reviewer_name: Mapped[str] = mapped_column(String(80), nullable=False)
    rating: Mapped[int | None] = mapped_column(UTinyInt)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Interaction(Base):
    __tablename__ = "interactions"
    __table_args__ = (
        Index("idx_interactions_user_time", "user_id", "occurred_at"),
        Index("idx_interactions_reviewer", "source_reviewer_id"),
        Index("idx_interactions_listing", "listing_id"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        UBigInt, ForeignKey("users.id", name="fk_interactions_user")
    )
    source_reviewer_id: Mapped[int | None] = mapped_column(UBigInt)
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_interactions_listing", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(enum(*INTERACTION_TYPES), nullable=False)
    weight: Mapped[Decimal] = mapped_column(DECIMAL(4, 2), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
