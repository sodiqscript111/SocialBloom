"""Add saved_creators table

Revision ID: a1b2c3d4e5f6
Revises: 0b84882af99c
Create Date: 2024-12-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0b84882af99c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('saved_creators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('saved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_creators_business_id'), 'saved_creators', ['business_id'], unique=False)
    op.create_index(op.f('ix_saved_creators_creator_id'), 'saved_creators', ['creator_id'], unique=False)
    op.create_index(op.f('ix_saved_creators_id'), 'saved_creators', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_creators_id'), table_name='saved_creators')
    op.drop_index(op.f('ix_saved_creators_creator_id'), table_name='saved_creators')
    op.drop_index(op.f('ix_saved_creators_business_id'), table_name='saved_creators')
    op.drop_table('saved_creators')
