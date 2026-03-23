"""create user events table

Revision ID: 002_create_user_events_table
Revises: 001_create_articles_table
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa

revision = "002_create_user_events_table"
down_revision = "001_create_articles_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("article_id", sa.String(length=36), sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_lat", sa.Float(), nullable=False),
        sa.Column("user_lon", sa.Float(), nullable=False),
        sa.Column("bucket_id", sa.String(length=64), nullable=False),
        sa.Column("event_weight", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_events_user_id", "user_events", ["user_id"])
    op.create_index("ix_user_events_session_id", "user_events", ["session_id"])
    op.create_index("ix_user_events_article_id", "user_events", ["article_id"])
    op.create_index("ix_user_events_event_type", "user_events", ["event_type"])
    op.create_index("ix_user_events_event_ts", "user_events", ["event_ts"])
    op.create_index("ix_user_events_bucket_id", "user_events", ["bucket_id"])
    op.create_index("ix_user_events_bucket_time", "user_events", ["bucket_id", "event_ts"])
    op.create_index("ix_user_events_article_time", "user_events", ["article_id", "event_ts"])


def downgrade() -> None:
    op.drop_index("ix_user_events_article_time", table_name="user_events")
    op.drop_index("ix_user_events_bucket_time", table_name="user_events")
    op.drop_index("ix_user_events_bucket_id", table_name="user_events")
    op.drop_index("ix_user_events_event_ts", table_name="user_events")
    op.drop_index("ix_user_events_event_type", table_name="user_events")
    op.drop_index("ix_user_events_article_id", table_name="user_events")
    op.drop_index("ix_user_events_session_id", table_name="user_events")
    op.drop_index("ix_user_events_user_id", table_name="user_events")
    op.drop_table("user_events")
