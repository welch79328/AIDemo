"""Add AI integration fields to Visit model

Revision ID: 75312805a79b
Revises: 20260327_slm
Create Date: 2026-03-27 17:37:48.660893+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75312805a79b'
down_revision = '20260327_slm'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to visits table
    op.add_column('visits', sa.Column('conversation_transcript', sa.Text(), nullable=True))
    op.add_column('visits', sa.Column('ai_analyzed', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('visits', sa.Column('interaction_id', sa.String(36), nullable=True))
    op.add_column('visits', sa.Column('ai_analysis_id', sa.String(36), nullable=True))

    # Add foreign key constraints
    op.create_foreign_key(
        'fk_visits_interaction_id',
        'visits', 'interactions',
        ['interaction_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_visits_ai_analysis_id',
        'visits', 'ai_analyses',
        ['ai_analysis_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_visits_ai_analysis_id', 'visits', type_='foreignkey')
    op.drop_constraint('fk_visits_interaction_id', 'visits', type_='foreignkey')

    # Drop columns
    op.drop_column('visits', 'ai_analysis_id')
    op.drop_column('visits', 'interaction_id')
    op.drop_column('visits', 'ai_analyzed')
    op.drop_column('visits', 'conversation_transcript')
