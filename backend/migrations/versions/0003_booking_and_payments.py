"""booking and payments: bookings, booking nights, payments, stripe events

Revision ID: 0003_booking_and_payments
Revises: 0002_reference_and_catalog
Create Date: 2026-10-19

Rules: BR-BKG, BR-PRC, BR-PAY, BR-STS, BR-CAN in docs/04-business-rules.md
"""

from alembic import op


revision = "0003_booking_and_payments"
down_revision = "0002_reference_and_catalog"
branch_labels = None
depends_on = None


CREATE_TABLES = [
    # Prices are a snapshot taken at hold time (BR-BKG-10).
    # check_out is exclusive. A held booking must have an expiry (BR-BKG-09).
    r"""
CREATE TABLE `bookings` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `code` char(8) NOT NULL,
  `user_id` bigint unsigned NOT NULL,
  `listing_id` bigint unsigned NOT NULL,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `guests` smallint unsigned NOT NULL,
  `status` enum('held','confirmed','completed','cancelled','expired') NOT NULL DEFAULT 'held',
  `nights` smallint unsigned NOT NULL,
  `nightly_usd` decimal(10,2) NOT NULL,
  `subtotal_usd` decimal(10,2) NOT NULL,
  `discount_usd` decimal(10,2) NOT NULL DEFAULT '0.00',
  `cleaning_usd` decimal(10,2) NOT NULL DEFAULT '0.00',
  `service_fee_usd` decimal(10,2) NOT NULL,
  `tax_usd` decimal(10,2) NOT NULL,
  `total_usd` decimal(10,2) NOT NULL,
  `display_currency` char(3) NOT NULL DEFAULT 'USD',
  `fx_rate` decimal(14,6) NOT NULL DEFAULT '1.000000',
  `cancellation_policy` enum('flexible','moderate','strict') NOT NULL,
  `refund_usd` decimal(10,2) DEFAULT NULL,
  `hold_expires_at` datetime DEFAULT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `cancel_reason` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bookings_code` (`code`),
  KEY `idx_bookings_user_created` (`user_id`,`created_at`),
  KEY `idx_bookings_listing_status` (`listing_id`,`status`,`check_in`,`check_out`),
  KEY `idx_bookings_status_hold` (`status`,`hold_expires_at`),
  CONSTRAINT `fk_bookings_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_bookings_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`),
  CONSTRAINT `ck_bookings_dates` CHECK (`check_out` > `check_in`),
  CONSTRAINT `ck_bookings_nights` CHECK (`nights` BETWEEN 1 AND 30),
  CONSTRAINT `ck_bookings_guests` CHECK (`guests` >= 1),
  CONSTRAINT `ck_bookings_money` CHECK (`total_usd` >= 0 AND `discount_usd` >= 0),
  CONSTRAINT `ck_bookings_refund` CHECK (`refund_usd` IS NULL OR (`refund_usd` >= 0 AND `refund_usd` <= `total_usd`)),
  CONSTRAINT `ck_bookings_hold` CHECK (`status` <> 'held' OR `hold_expires_at` IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # The double-booking guard (BR-BKG-11). One row per occupied night.
    # The primary key (listing_id, night) makes it impossible for two bookings
    # to hold the same night, even when requests arrive at the same moment.
    # Rows are deleted when a booking expires or is cancelled (BR-STS-03).
    r"""
CREATE TABLE `booking_nights` (
  `listing_id` bigint unsigned NOT NULL,
  `night` date NOT NULL,
  `booking_id` bigint unsigned NOT NULL,
  PRIMARY KEY (`listing_id`,`night`),
  KEY `idx_booking_nights_booking` (`booking_id`),
  CONSTRAINT `fk_booking_nights_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_booking_nights_booking` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `payments` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `booking_id` bigint unsigned NOT NULL,
  `provider` enum('stripe') NOT NULL DEFAULT 'stripe',
  `provider_ref` varchar(255) NOT NULL,
  `kind` enum('charge','refund') NOT NULL,
  `amount_usd` decimal(10,2) NOT NULL,
  `status` enum('pending','succeeded','failed','refunded') NOT NULL DEFAULT 'pending',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_payments_provider_ref` (`provider`,`provider_ref`),
  KEY `idx_payments_booking` (`booking_id`),
  CONSTRAINT `fk_payments_booking` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`),
  CONSTRAINT `ck_payments_amount` CHECK (`amount_usd` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Each Stripe webhook event is processed once (BR-PAY-03).
    r"""
CREATE TABLE `stripe_events` (
  `event_id` varchar(255) NOT NULL,
  `type` varchar(80) NOT NULL,
  `received_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "stripe_events",
    "payments",
    "booking_nights",
    "bookings",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
