from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    DECIMAL,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from models.types import Bool, UBigInt, UInt, USmallInt, UTinyInt, enum

AMENITY_CATEGORIES = (
    "essentials", "kitchen", "work", "outdoor", "safety",
    "family", "parking", "entertainment", "other",
)
ROOM_TYPES = ("entire_home", "private_room", "shared_room", "hotel_room")
CANCELLATION_POLICIES = ("flexible", "moderate", "strict")
PHOTO_SOURCES = ("pexels", "unsplash")
BLOCK_REASONS = ("host", "maintenance")


class FxRate(Base):
    __tablename__ = "fx_rates"

    currency: Mapped[str] = mapped_column(CHAR(3), primary_key=True)
    usd_rate: Mapped[Decimal] = mapped_column(DECIMAL(14, 6), nullable=False)
    as_of: Mapped[date] = mapped_column(Date, nullable=False)


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("slug", name="uq_cities_slug"),)

    id: Mapped[int] = mapped_column(UInt, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    region: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    timezone: Mapped[str] = mapped_column(String(40), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(DECIMAL(5, 4), nullable=False)
    lat: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    lng: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(255))
    snapshot_date: Mapped[date | None] = mapped_column(Date)
    cover_photo_url: Mapped[str | None] = mapped_column(String(500))
    cover_photo_credit: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Bool, nullable=False, server_default=text("'1'"))


class Amenity(Base):
    __tablename__ = "amenities"
    __table_args__ = (UniqueConstraint("name", name="uq_amenities_name"),)

    id: Mapped[int] = mapped_column(UInt, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(
        enum(*AMENITY_CATEGORIES), nullable=False, server_default="other"
    )
    is_filter: Mapped[bool] = mapped_column(Bool, nullable=False, server_default=text("'0'"))


class Host(Base):
    __tablename__ = "hosts"
    __table_args__ = (UniqueConstraint("source_host_id", name="uq_hosts_source"),)

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    source_host_id: Mapped[int] = mapped_column(UBigInt, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_superhost: Mapped[bool] = mapped_column(Bool, nullable=False, server_default=text("'0'"))
    host_since: Mapped[date | None] = mapped_column(Date)
    response_rate: Mapped[int | None] = mapped_column(UTinyInt)
    listings_count: Mapped[int] = mapped_column(UInt, nullable=False, server_default=text("'1'"))


class ListingAmenity(Base):
    __tablename__ = "listing_amenities"
    __table_args__ = (Index("idx_listing_amenities_amenity", "amenity_id"),)

    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_listing_amenities_listing", ondelete="CASCADE"),
        primary_key=True,
    )
    amenity_id: Mapped[int] = mapped_column(
        UInt,
        ForeignKey("amenities.id", name="fk_listing_amenities_amenity", ondelete="CASCADE"),
        primary_key=True,
    )


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("source_listing_id", name="uq_listings_source"),
        Index("idx_listings_city_active_price", "city_id", "is_active", "nightly_price_usd"),
        Index("idx_listings_city_popularity", "city_id", "popularity_score"),
        Index("idx_listings_geo", "lat", "lng"),
        Index("idx_listings_room_type", "room_type"),
        Index("idx_listings_host", "host_id"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    source_listing_id: Mapped[int] = mapped_column(UBigInt, nullable=False)
    city_id: Mapped[int] = mapped_column(
        UInt, ForeignKey("cities.id", name="fk_listings_city"), nullable=False
    )
    host_id: Mapped[int] = mapped_column(
        UBigInt, ForeignKey("hosts.id", name="fk_listings_host"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    neighbourhood: Mapped[str | None] = mapped_column(String(120))
    lat: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    lng: Mapped[Decimal] = mapped_column(DECIMAL(9, 6), nullable=False)
    property_type: Mapped[str] = mapped_column(String(80), nullable=False)
    room_type: Mapped[str] = mapped_column(enum(*ROOM_TYPES), nullable=False)
    accommodates: Mapped[int] = mapped_column(USmallInt, nullable=False)
    bedrooms: Mapped[int | None] = mapped_column(USmallInt)
    beds: Mapped[int | None] = mapped_column(USmallInt)
    bathrooms: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 1))
    nightly_price_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    nightly_price_local: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    cleaning_fee_usd: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2), nullable=False, server_default=text("'0.00'")
    )
    min_nights: Mapped[int] = mapped_column(USmallInt, nullable=False, server_default=text("'1'"))
    max_nights: Mapped[int] = mapped_column(USmallInt, nullable=False, server_default=text("'30'"))
    cancellation_policy: Mapped[str] = mapped_column(enum(*CANCELLATION_POLICIES), nullable=False)
    check_in_time: Mapped[time] = mapped_column(Time, nullable=False, server_default=text("'15:00:00'"))
    check_out_time: Mapped[time] = mapped_column(Time, nullable=False, server_default=text("'11:00:00'"))
    instant_bookable: Mapped[bool] = mapped_column(Bool, nullable=False, server_default=text("'1'"))
    rating_overall: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2))
    rating_cleanliness: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2))
    rating_location: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2))
    rating_value: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2))
    rating_communication: Mapped[Decimal | None] = mapped_column(DECIMAL(3, 2))
    review_count: Mapped[int] = mapped_column(UInt, nullable=False, server_default=text("'0'"))
    popularity_score: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 4), nullable=False, server_default=text("'0.0000'")
    )
    is_active: Mapped[bool] = mapped_column(Bool, nullable=False, server_default=text("'1'"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    city: Mapped[City] = relationship(lazy="joined")
    host: Mapped[Host] = relationship()
    photos: Mapped[list[ListingPhoto]] = relationship(order_by="ListingPhoto.position")
    amenities: Mapped[list[Amenity]] = relationship(secondary="listing_amenities")


class ListingPhoto(Base):
    __tablename__ = "listing_photos"
    __table_args__ = (Index("idx_listing_photos_listing", "listing_id", "position"),)

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_listing_photos_listing", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumb_url: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[int | None] = mapped_column(USmallInt)
    height: Mapped[int | None] = mapped_column(USmallInt)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=False)
    photographer: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str] = mapped_column(enum(*PHOTO_SOURCES), nullable=False)
    source_page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(UTinyInt, nullable=False, server_default=text("'0'"))


class ListingBlock(Base):
    """Host-blocked dates. end_date is exclusive (BR-AVL-01)."""

    __tablename__ = "listing_blocks"
    __table_args__ = (
        Index("idx_listing_blocks_range", "listing_id", "start_date", "end_date"),
    )

    id: Mapped[int] = mapped_column(UBigInt, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        UBigInt,
        ForeignKey("listings.id", name="fk_listing_blocks_listing", ondelete="CASCADE"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(enum(*BLOCK_REASONS), nullable=False, server_default="host")
