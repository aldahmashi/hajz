"""identity: users, refresh tokens, email tokens

Revision ID: 0001_identity
Revises: None
Create Date: 2026-10-19

Rules: BR-ACC in docs/04-business-rules.md
"""

from alembic import op


revision = "0001_identity"
down_revision = None
branch_labels = None
depends_on = None


CREATE_TABLES = [
    # Demo personas have no password (one-click login, BR-DEMO-01).
    # Real users must have one unless the account was deleted (BR-ACC-13).
    r"""
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `full_name` varchar(120) NOT NULL,
  `role` enum('guest','admin') NOT NULL DEFAULT 'guest',
  `is_demo` tinyint(1) NOT NULL DEFAULT '0',
  `persona_key` varchar(40) DEFAULT NULL,
  `persona_summary` varchar(255) DEFAULT NULL,
  `email_verified_at` datetime DEFAULT NULL,
  `preferred_currency` char(3) NOT NULL DEFAULT 'USD',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_email` (`email`),
  UNIQUE KEY `uq_users_persona_key` (`persona_key`),
  CONSTRAINT `ck_users_password` CHECK (
    (`is_demo` = 1 AND `password_hash` IS NULL)
    OR (`is_demo` = 0 AND (`password_hash` IS NOT NULL OR `deleted_at` IS NOT NULL))
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Refresh tokens are stored hashed and rotated. A family groups one login
    # session so reuse of a revoked token can revoke the whole family (BR-ACC-10).
    r"""
CREATE TABLE `refresh_tokens` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `family_id` char(32) NOT NULL,
  `token_hash` char(64) NOT NULL,
  `expires_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  `replaced_by_id` bigint unsigned DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `ip_hash` char(64) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_refresh_tokens_hash` (`token_hash`),
  KEY `idx_refresh_tokens_user` (`user_id`),
  KEY `idx_refresh_tokens_family` (`family_id`),
  CONSTRAINT `fk_refresh_tokens_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
    # Single-use verification and password-reset tokens (BR-ACC-05, BR-ACC-06).
    r"""
CREATE TABLE `email_tokens` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `purpose` enum('verify','reset') NOT NULL,
  `token_hash` char(64) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_email_tokens_hash` (`token_hash`),
  KEY `idx_email_tokens_user_purpose` (`user_id`,`purpose`),
  CONSTRAINT `fk_email_tokens_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
""",
]

DROP_TABLES = [
    "email_tokens",
    "refresh_tokens",
    "users",
]


def upgrade() -> None:
    for statement in CREATE_TABLES:
        op.execute(statement)


def downgrade() -> None:
    for table in DROP_TABLES:
        op.execute(f"DROP TABLE IF EXISTS `{table}`")
