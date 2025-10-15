"""add_tips_performance_indexes

Revision ID: 2de14fa211e9
Revises: 105f096d67eb
Create Date: 2025-10-15 07:12:55.833403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2de14fa211e9'
down_revision: Union[str, Sequence[str], None] = '105f096d67eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Add performance indexes for tips table."""
    # 복합 인덱스: publish_date + is_active (get_daily_tip 쿼리 최적화)
    op.create_index(
        'idx_tips_publish_date_active',
        'tips',
        ['publish_date', 'is_active'],
        schema='linux_tips'
    )

    # 단일 인덱스: difficulty (필터링 최적화)
    op.create_index(
        'idx_tips_difficulty',
        'tips',
        ['difficulty'],
        schema='linux_tips'
    )

    # JSONB GIN 인덱스: category 배열 검색 최적화
    op.execute("""
        CREATE INDEX idx_tips_category_gin
        ON linux_tips.tips USING gin (category);
    """)


def downgrade() -> None:
    """Downgrade schema: Remove performance indexes."""
    # 인덱스 역순으로 삭제
    op.execute("DROP INDEX IF EXISTS linux_tips.idx_tips_category_gin;")
    op.drop_index('idx_tips_difficulty', table_name='tips', schema='linux_tips')
    op.drop_index('idx_tips_publish_date_active', table_name='tips', schema='linux_tips')
