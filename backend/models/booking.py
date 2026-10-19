from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    DECIMAL,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.catalog import CANCELLATION_POLICIES, Listing
from models.identity import User
from models.types import UBigInt, USmallInt, enum

BOOKING_STATUSES = ("held", "confirmed", "completed", "cancelled", "expired")
PAYMENT_PROVIDERS = ("stripe",)
PAYMENT_KINDS = ("charge", "refund")
PAYMENT_STATUSES = ("pending", "succeeded", "failed", "refunded")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("code", name="uq_bookings_code"),
        Index("idx_bookings_user_created", "user_id", "created_at"),
        Index("idx_bookings_listing_status", "listing_id", "status", "check_in", "check_out"),
        Index("idx_bookings_status_hold", "status", "hold_expires_at"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(CHAR(8), nullable=False)
    user_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("users.id", name="fk_bookings_user"), nullable=False
    )
    listing_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("listings.id", name="fk_bookings_listing"), nullable=False
    )
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guests: Mapped[int] = mapped_column(USmallInt, nullable=False)
    status: Mapped[str] = mapped_column(enum(*BOOKING_STATUSES), nullable=False, server_default="held")
    nights: Mapped[int] = mapped_column(USmallInt, nullable=False)
    nightly_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    subtotal_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    discount_usd: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, server_default=text("'0.00'")
    )
    cleaning_usd: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, server_default=text("'0.00'")
    )
    service_fee_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    tax_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    total_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    display_currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, server_default="USD")
    fx_rate: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 6), nullable=False, server_default=text("'1.000000'")
    )
    cancellation_policy: Mapped[str] = mapped_column(enum(*CANCELLATION_POLICIES), nullable=False)
    refund_usd: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    hold_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancel_reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    user: Mapped[User] = relationship()
    listing: Mapped[Listing] = relationship()


class BookingNight(Base):
    """One row per occupied night: the double-booking guard (BR-BKG-11)."""

    __tablename__ = "booking_nights"
    __table_args__ = (Index("idx_booking_nights_booking", "booking_id"),)

    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_booking_nights_listing", ondelete="CASCADE"),
        primary_key=True,
    )
    night: Mapped[date] = mapped_column(Date, primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("bookings.id", name="fk_booking_nights_booking", ondelete="CASCADE"),
        nullable=False,
    )


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("provider", "provider_ref", name="uq_payments_provider_ref"),
        Index("idx_payments_booking", "booking_id"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("bookings.id", name="fk_payments_booking"), nullable=False
    )
    provider: Mapped[str] = mapped_column(enum(*PAYMENT_PROVIDERS), nullable=False, server_default="stripe")
    provider_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(enum(*PAYMENT_KINDS), nullable=False)
    amount_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(enum(*PAYMENT_STATUSES), nullable=False, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )


class StripeEvent(Base):
    __tablename__ = "stripe_events"

    event_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
