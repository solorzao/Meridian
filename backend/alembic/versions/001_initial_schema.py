"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("azure_ad_b2c_id", sa.String(128), nullable=False),
        sa.Column("email", sa.String(256), nullable=False),
        sa.Column("display_name", sa.String(256), nullable=False),
        sa.Column("subscription_tier", sa.String(20), nullable=False, server_default="Free"),
        sa.Column("stripe_customer_id", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("azure_ad_b2c_id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("entry_date", sa.DateTime(), nullable=False),
        sa.Column("entry_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("exit_date", sa.DateTime(), nullable=True),
        sa.Column("exit_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("position_size", sa.Numeric(18, 4), nullable=False),
        sa.Column("stop_loss", sa.Numeric(18, 4), nullable=True),
        sa.Column("take_profit", sa.Numeric(18, 4), nullable=True),
        sa.Column("pnl", sa.Numeric(18, 4), nullable=True),
        sa.Column("pnl_percent", sa.Numeric(18, 4), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="Open"),
        sa.Column("thesis", sa.String(2000), nullable=True),
        sa.Column("emotional_state", sa.String(100), nullable=True),
        sa.Column("market_conditions", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trades_user_status", "trades", ["user_id", "status"])
    op.create_index("ix_trades_user_entry_date", "trades", ["user_id", "entry_date"])

    op.create_table(
        "strategies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("source", sa.String(10), nullable=False, server_default="user"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_strategies_user_name"),
    )

    op.create_table(
        "trade_strategy_tags",
        sa.Column("trade_id", sa.UUID(), nullable=False),
        sa.Column("strategy_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(10), nullable=False, server_default="user"),
        sa.ForeignKeyConstraint(["trade_id"], ["trades.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["strategy_id"], ["strategies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("trade_id", "strategy_id"),
    )

    op.create_table(
        "trade_screenshots",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("trade_id", sa.UUID(), nullable=False),
        sa.Column("blob_url", sa.String(1024), nullable=False),
        sa.Column("caption", sa.String(500), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trade_id"], ["trades.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("messages", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"])

    op.create_table(
        "agent_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("agent_type", sa.String(20), nullable=False),
        sa.Column("custom_system_prompt", sa.Text(), nullable=True),
        sa.Column("settings", postgresql.JSONB(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_configs_user_id", "agent_configs", ["user_id"])

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("trading_style", sa.String(50), nullable=True),
        sa.Column("preferred_sectors", postgresql.JSONB(), nullable=True),
        sa.Column("watchlist_tickers", postgresql.JSONB(), nullable=True),
        sa.Column("strategy_performance", postgresql.JSONB(), nullable=True),
        sa.Column("risk_profile", sa.String(50), nullable=True),
        sa.Column("last_refreshed", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.drop_table("agent_configs")
    op.drop_table("conversations")
    op.drop_table("trade_screenshots")
    op.drop_table("trade_strategy_tags")
    op.drop_table("strategies")
    op.drop_table("trades")
    op.drop_table("users")
