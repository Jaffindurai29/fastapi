"""create migrated_items

Revision ID: 0001
Revises:
Create Date: 2026-10-05 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None  # first migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The table as it looked on day one: no description column yet.
    items = op.create_table(
        "migrated_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # Seed data lives here, not in main.py: it runs exactly once, when
    # the table is created, and disappears with it on downgrade.
    op.bulk_insert(
        items,
        [
            {"name": "Laptop", "price": 999.99},
            {"name": "Mouse", "price": 19.99},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("migrated_items")
