"""create articles table

Revision ID: 001_create_articles_table
Revises:
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa

revision = "001_create_articles_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("publication_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.JSON(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("llm_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_articles_source_name", "articles", ["source_name"])
    op.create_index("ix_articles_relevance_score", "articles", ["relevance_score"])


def downgrade() -> None:
    op.drop_index("ix_articles_relevance_score", table_name="articles")
    op.drop_index("ix_articles_source_name", table_name="articles")
    op.drop_table("articles")
