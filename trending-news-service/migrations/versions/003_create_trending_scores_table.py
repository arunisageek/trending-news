"""create trending scores table

Revision ID: 003_create_trending_scores_table
Revises: 002_create_user_events_table
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa

revision = "003_create_trending_scores_table"
down_revision = "002_create_user_events_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trending_scores",
        sa.Column("bucket_id", sa.String(length=64), primary_key=True),
        sa.Column("article_id", sa.String(length=36), sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("score_window", sa.String(length=20), primary_key=True),
        sa.Column("trend_score", sa.Float(), nullable=False),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("shares_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bookmarks_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_event_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_trending_scores_lookup", "trending_scores", ["bucket_id", "score_window", "trend_score"])
    op.create_index("ix_trending_scores_computed_at", "trending_scores", ["computed_at"])


def downgrade() -> None:
    op.drop_index("ix_trending_scores_computed_at", table_name="trending_scores")
    op.drop_index("ix_trending_scores_lookup", table_name="trending_scores")
    op.drop_table("trending_scores")
