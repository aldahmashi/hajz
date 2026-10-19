"""reference data and catalogue: fx rates, cities, amenities, hosts, listings

Revision ID: 0002_reference_and_catalog
Revises: 0001_identity
Create Date: 2026-10-19

Tables: fx_rates, cities, amenities, hosts, listings, listing_amenities,
        listing_photos, listing_blocks
Rules: BR-CAT, BR-AVL-01, BR-PRC-03, BR-IMP in docs/04-business-rules.md
"""

from alembic import op


revision = "0002_reference_and_catalog"
down_revision = "0001_identity"
branch_labels = None
depends_on = None


CREATE_TABLES = [
    # Units of currency per 1 USD. Money is stored in USD (BR-PRC-02).
    r"""
CREATE TABLE `fx_rates` (
  `currency` char(3) NOT NULL,
  `usd_rate` decimal(14,6) NOT NULL,
  `as_of` date NOT NULL,
  PRIMARY KEY (`currency`),
  CONSTRAINT `ck_fx_rates_positive` CHECK (`usd_rate` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # tax_rate is a simplified demo value between 0 and 30 percent (BR-PRC-03).
    r"""
CREATE TABLE `cities` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `slug` varchar(40) NOT NULL,
  `name` varchar(80) NOT NULL,
  `country` varchar(80) NOT NULL,
  `country_code` char(2) NOT NULL,
  `region` varchar(40) NOT NULL,
  `currency` char(3) NOT NULL,
  `timezone` varchar(40) NOT NULL,
  `tax_rate` decimal(5,4) NOT NULL,
  `lat` decimal(9,6) NOT NULL,
  `lng` decimal(9,6) NOT NULL,
  `source_url` varchar(255) DEFAULT NULL,
  `snapshot_date` date DEFAULT NULL,
  `cover_photo_url` varchar(500) DEFAULT NULL,
  `cover_photo_credit` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_cities_slug` (`slug`),
  CONSTRAINT `ck_cities_tax_rate` CHECK (`tax_rate` >= 0 AND `tax_rate` <= 0.3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `amenities` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  `category` enum('essentials','kitchen','work','outdoor','safety','family','parking','entertainment','other') NOT NULL DEFAULT 'other',
  `is_filter` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_amenities_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `hosts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `source_host_id` bigint unsigned NOT NULL,
  `name` varchar(120) NOT NULL,
  `is_superhost` tinyint(1) NOT NULL DEFAULT '0',
  `host_since` date DEFAULT NULL,
  `response_rate` tinyint unsigned DEFAULT NULL,
  `listings_count` int unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_hosts_source` (`source_host_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Prices in USD (converted at import) plus the original local price.
    # Nights are capped at 30 (BR-IMP-04, BR-BKG-05).
    r"""
CREATE TABLE `listings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `source_listing_id` bigint unsigned NOT NULL,
  `city_id` int unsigned NOT NULL,
  `host_id` bigint unsigned NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `neighbourhood` varchar(120) DEFAULT NULL,
  `lat` decimal(9,6) NOT NULL,
  `lng` decimal(9,6) NOT NULL,
  `property_type` varchar(80) NOT NULL,
  `room_type` enum('entire_home','private_room','shared_room','hotel_room') NOT NULL,
  `accommodates` smallint unsigned NOT NULL,
  `bedrooms` smallint unsigned DEFAULT NULL,
  `beds` smallint unsigned DEFAULT NULL,
  `bathrooms` decimal(3,1) DEFAULT NULL,
  `nightly_price_usd` decimal(10,2) NOT NULL,
  `nightly_price_local` decimal(12,2) NOT NULL,
  `cleaning_fee_usd` decimal(10,2) NOT NULL DEFAULT '0.00',
  `min_nights` smallint unsigned NOT NULL DEFAULT '1',
  `max_nights` smallint unsigned NOT NULL DEFAULT '30',
  `cancellation_policy` enum('flexible','moderate','strict') NOT NULL,
  `check_in_time` time NOT NULL DEFAULT '15:00:00',
  `check_out_time` time NOT NULL DEFAULT '11:00:00',
  `instant_bookable` tinyint(1) NOT NULL DEFAULT '1',
  `rating_overall` decimal(3,2) DEFAULT NULL,
  `rating_cleanliness` decimal(3,2) DEFAULT NULL,
  `rating_location` decimal(3,2) DEFAULT NULL,
  `rating_value` decimal(3,2) DEFAULT NULL,
  `rating_communication` decimal(3,2) DEFAULT NULL,
  `review_count` int unsigned NOT NULL DEFAULT '0',
  `popularity_score` decimal(8,4) NOT NULL DEFAULT '0.0000',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_listings_source` (`source_listing_id`),
  KEY `idx_listings_city_active_price` (`city_id`,`is_active`,`nightly_price_usd`),
  KEY `idx_listings_city_popularity` (`city_id`,`popularity_score`),
  KEY `idx_listings_geo` (`lat`,`lng`),
  KEY `idx_listings_room_type` (`room_type`),
  KEY `idx_listings_host` (`host_id`),
  CONSTRAINT `fk_listings_city` FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`),
  CONSTRAINT `fk_listings_host` FOREIGN KEY (`host_id`) REFERENCES `hosts` (`id`),
  CONSTRAINT `ck_listings_price` CHECK (`nightly_price_usd` > 0 AND `cleaning_fee_usd` >= 0),
  CONSTRAINT `ck_listings_accommodates` CHECK (`accommodates` >= 1),
  CONSTRAINT `ck_listings_nights` CHECK (`min_nights` >= 1 AND `max_nights` <= 30 AND `min_nights` <= `max_nights`),
  CONSTRAINT `ck_listings_rating` CHECK (`rating_overall` IS NULL OR (`rating_overall` >= 0 AND `rating_overall` <= 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `listing_amenities` (
  `listing_id` bigint unsigned NOT NULL,
  `amenity_id` int unsigned NOT NULL,
  PRIMARY KEY (`listing_id`,`amenity_id`),
  KEY `idx_listing_amenities_amenity` (`amenity_id`),
  CONSTRAINT `fk_listing_amenities_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_listing_amenities_amenity` FOREIGN KEY (`amenity_id`) REFERENCES `amenities` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Licensed photos (Pexels / Unsplash) with attribution (DA-3).
    r"""
CREATE TABLE `listing_photos` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `listing_id` bigint unsigned NOT NULL,
  `url` varchar(500) NOT NULL,
  `thumb_url` varchar(500) NOT NULL,
  `width` smallint unsigned DEFAULT NULL,
  `height` smallint unsigned DEFAULT NULL,
  `alt_text` varchar(255) NOT NULL,
  `photographer` varchar(120) NOT NULL,
  `source` enum('pexels','unsplash') NOT NULL,
  `source_page_url` varchar(500) NOT NULL,
  `position` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_listing_photos_listing` (`listing_id`,`position`),
  CONSTRAINT `fk_listing_photos_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Host-blocked date ranges. end_date is exclusive (BR-AVL-01).
    r"""
CREATE TABLE `listing_blocks` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `listing_id` bigint unsigned NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `reason` enum('host','maintenance') NOT NULL DEFAULT 'host',
  PRIMARY KEY (`id`),
  KEY `idx_listing_blocks_range` (`listing_id`,`start_date`,`end_date`),
  CONSTRAINT `fk_listing_blocks_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_listing_blocks_range` CHECK (`end_date` > `start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "listing_blocks",
    "listing_photos",
    "listing_amenities",
    "listings",
    "hosts",
    "amenities",
    "cities",
    "fx_rates",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
