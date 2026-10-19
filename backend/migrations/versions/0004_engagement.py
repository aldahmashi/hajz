"""engagement: wishlist, reviews, interactions

Revision ID: 0004_engagement
Revises: 0003_booking_and_payments
Create Date: 2026-10-19

Rules: BR-WSH, BR-REV, BR-REC-01, BR-REC-02 in docs/04-business-rules.md
"""

from alembic import op


revision = "0004_engagement"
down_revision = "0003_booking_and_payments"
branch_labels = None
depends_on = None


CREATE_TABLES = [
    r"""
CREATE TABLE `wishlist_items` (
  `user_id` bigint unsigned NOT NULL,
  `listing_id` bigint unsigned NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`listing_id`),
  KEY `idx_wishlist_items_listing` (`listing_id`),
  CONSTRAINT `fk_wishlist_items_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wishlist_items_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Imported reviews come from Inside Airbnb and have no star rating.
    # App reviews belong to one completed booking and must have a 1-5 rating
    # (BR-REV-02, BR-REV-04). MySQL allows many NULLs in a UNIQUE key, so
    # imported reviews (booking_id NULL) do not collide.
    r"""
CREATE TABLE `reviews` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `listing_id` bigint unsigned NOT NULL,
  `source` enum('imported','app') NOT NULL,
  `source_review_id` bigint unsigned DEFAULT NULL,
  `booking_id` bigint unsigned DEFAULT NULL,
  `user_id` bigint unsigned DEFAULT NULL,
  `reviewer_name` varchar(80) NOT NULL,
  `rating` tinyint unsigned DEFAULT NULL,
  `comment` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_reviews_booking` (`booking_id`),
  UNIQUE KEY `uq_reviews_source` (`source_review_id`),
  KEY `idx_reviews_listing_created` (`listing_id`,`created_at`),
  KEY `idx_reviews_user` (`user_id`),
  CONSTRAINT `fk_reviews_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_reviews_booking` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_reviews_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `ck_reviews_rating` CHECK (`rating` IS NULL OR `rating` BETWEEN 1 AND 5),
  CONSTRAINT `ck_reviews_source` CHECK (
    (`source` = 'imported' AND `source_review_id` IS NOT NULL)
    OR (`source` = 'app' AND `rating` IS NOT NULL)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Training signal for the recommender (BR-REC-01). Each row belongs to an
    # app user OR an imported (pseudonymous) Inside Airbnb reviewer, never both.
    # fk_interactions_user has no ON DELETE action because MySQL forbids
    # actions on a column used in a CHECK. Users are soft-deleted and their
    # interactions are removed by the service (BR-ACC-13).
    r"""
CREATE TABLE `interactions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned DEFAULT NULL,
  `source_reviewer_id` bigint unsigned DEFAULT NULL,
  `listing_id` bigint unsigned NOT NULL,
  `type` enum('view','save','book','review','imported_stay') NOT NULL,
  `weight` decimal(4,2) NOT NULL,
  `occurred_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_interactions_user_time` (`user_id`,`occurred_at`),
  KEY `idx_interactions_reviewer` (`source_reviewer_id`),
  KEY `idx_interactions_listing` (`listing_id`),
  CONSTRAINT `fk_interactions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_interactions_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_interactions_actor` CHECK (
    (`user_id` IS NOT NULL AND `source_reviewer_id` IS NULL)
    OR (`user_id` IS NULL AND `source_reviewer_id` IS NOT NULL)
  ),
  CONSTRAINT `ck_interactions_weight` CHECK (`weight` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "interactions",
    "reviews",
    "wishlist_items",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
