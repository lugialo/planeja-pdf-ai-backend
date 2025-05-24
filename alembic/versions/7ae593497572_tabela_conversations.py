"""Tabela conversations

Revision ID: 7ae593497572
Revises: 
Create Date: 2025-05-02 23:58:49.334073

"""
from typing import Sequence, Union

from alembic import op
from datetime import datetime
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ae593497572'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criação da tabela sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Criação da tabela conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('session_id', sa.String(), sa.ForeignKey('sessions.id'), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove as tabelas na ordem inversa
    op.drop_table('conversations')
    op.drop_table('sessions')
