"""Split thesis into entry/exit thesis and add market sentiment

Revision ID: 002
Revises: 001
Create Date: 2026-02-14

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("trades", sa.Column("entry_thesis", sa.String(2000), nullable=True))
    op.add_column("trades", sa.Column("exit_thesis", sa.String(2000), nullable=True))
    op.add_column("trades", sa.Column("market_sentiment", sa.Integer(), nullable=True))

    # Migrate existing thesis data to entry_thesis
    op.execute("UPDATE trades SET entry_thesis = thesis")

    op.drop_column("trades", "thesis")


def downgrade() -> None:
    op.add_column("trades", sa.Column("thesis", sa.String(2000), nullable=True))

    # Copy entry_thesis back to thesis
    op.execute("UPDATE trades SET thesis = entry_thesis")

    op.drop_column("trades", "market_sentiment")
    op.drop_column("trades", "exit_thesis")
    op.drop_column("trades", "entry_thesis")
