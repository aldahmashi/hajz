"""machine learning: embeddings, ML runs, recommendations, review insights

Revision ID: 0005_ml
Revises: 0004_engagement
Create Date: 2026-10-19

Rules: BR-REC in docs/04-business-rules.md
"""

from alembic import op


revision = "0005_ml"
down_revision = "0004_engagement"
branch_labels = None
depends_on = None


CREATE_TABLES = [
    # float32 vector stored as raw bytes, loaded into NumPy by the API.
    r"""
CREATE TABLE `listing_embeddings` (
  `listing_id` bigint unsigned NOT NULL,
  `model` varchar(80) NOT NULL,
  `dim` smallint unsigned NOT NULL,
  `vector` mediumblob NOT NULL,
  `text_hash` char(64) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`listing_id`),
  CONSTRAINT `fk_listing_embeddings_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `ml_runs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` datetime DEFAULT NULL,
  `status` enum('running','succeeded','failed') NOT NULL DEFAULT 'running',
  `metrics` json DEFAULT NULL,
  `git_sha` char(40) DEFAULT NULL,
  `notes` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ml_runs_status_finished` (`status`,`finished_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Each run writes a full set. The API reads the latest succeeded run (BR-REC-07).
    r"""
CREATE TABLE `recommendations` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `run_id` bigint unsigned NOT NULL,
  `subject_type` enum('listing','user') NOT NULL,
  `subject_id` bigint unsigned NOT NULL,
  `kind` enum('similar','also_stayed','for_you','cross_city') NOT NULL,
  `listing_id` bigint unsigned NOT NULL,
  `position` smallint unsigned NOT NULL,
  `score` decimal(8,5) NOT NULL,
  `reason` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_recommendations_slot` (`run_id`,`subject_type`,`subject_id`,`kind`,`position`),
  KEY `idx_recommendations_lookup` (`subject_type`,`subject_id`,`kind`,`run_id`),
  KEY `idx_recommendations_listing` (`listing_id`),
  CONSTRAINT `fk_recommendations_run` FOREIGN KEY (`run_id`) REFERENCES `ml_runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_recommendations_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Phase 2 (AI-7).
    r"""
CREATE TABLE `listing_review_insights` (
  `listing_id` bigint unsigned NOT NULL,
  `loves` json NOT NULL,
  `watch_outs` json NOT NULL,
  `summary` text NOT NULL,
  `model` varchar(80) NOT NULL,
  `review_count_used` int unsigned NOT NULL,
  `generated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`listing_id`),
  CONSTRAINT `fk_listing_review_insights_listing` FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "listing_review_insights",
    "recommendations",
    "ml_runs",
    "listing_embeddings",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
