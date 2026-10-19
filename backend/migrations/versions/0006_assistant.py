"""AI assistant: chat sessions, chat messages, daily usage

Revision ID: 0006_assistant
Revises: 0005_ml
Create Date: 2026-10-19

Rules: BR-AI in docs/04-business-rules.md
"""

from alembic import op


revision = "0006_assistant"
down_revision = "0005_ml"
branch_labels = None
depends_on = None


CREATE_TABLES = [
    # id is a ULID (sortable, safe to expose). Visitors are identified by a
    # hashed anonymous key instead of a user id.
    r"""
CREATE TABLE `chat_sessions` (
  `id` char(26) NOT NULL,
  `user_id` bigint unsigned DEFAULT NULL,
  `anon_key_hash` char(64) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_active_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_chat_sessions_user` (`user_id`),
  KEY `idx_chat_sessions_last_active` (`last_active_at`),
  CONSTRAINT `fk_chat_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    r"""
CREATE TABLE `chat_messages` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `session_id` char(26) NOT NULL,
  `role` enum('user','assistant','tool') NOT NULL,
  `content` text NOT NULL,
  `tool_name` varchar(60) DEFAULT NULL,
  `tool_payload` json DEFAULT NULL,
  `cited_listing_ids` json DEFAULT NULL,
  `tokens_in` int unsigned DEFAULT NULL,
  `tokens_out` int unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_chat_messages_session` (`session_id`,`id`),
  CONSTRAINT `fk_chat_messages_session` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Daily quota counter per user id or hashed IP (BR-AI-01).
    r"""
CREATE TABLE `ai_usage_daily` (
  `subject_key` varchar(80) NOT NULL,
  `day` date NOT NULL,
  `requests` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`subject_key`,`day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "ai_usage_daily",
    "chat_messages",
    "chat_sessions",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
