"""enforce one wallet and one holding per user/coin

Revision ID: 8f2a9c1b7d44
Revises: 1753d05f6977
Create Date: 2026-11-12
"""
from alembic import op
import sqlalchemy as sa

revision = "8f2a9c1b7d44"
down_revision = "1753d05f6977"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_wallet_user",
        "wallet",
        ["user_id"],
    )
    op.create_unique_constraint(
        "uq_holding_user_coin",
        "holding",
        ["user_id", "coin_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_holding_user_coin", "holding", type_="unique")
    op.drop_constraint("uq_wallet_user", "wallet", type_="unique")
