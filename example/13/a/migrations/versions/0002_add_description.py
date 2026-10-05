"""add description

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-05 12:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"  # runs after 0001
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # nullable=True, so the rows that already exist simply get NULL.
    # batch_alter_table is what lets this also work on SQLite.
    with op.batch_alter_table("migrated_items") as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Throws away whatever was stored in description. That's what
    # "going back" means; make a backup first on a real database.
    with op.batch_alter_table("migrated_items") as batch_op:
        batch_op.drop_column("description")
