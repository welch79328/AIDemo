"""add sales lead management tables

Revision ID: 20260327_slm
Revises: 949902ff763d
Create Date: 2026-03-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260327_slm'
down_revision: Union[str, None] = '949902ff763d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 創建 import_batches 表（必須先創建，因為 customers 有外鍵參照）
    op.create_table(
        'import_batches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('PROCESSING', 'COMPLETED', 'FAILED', name='importstatus'), nullable=False),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fail_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicate_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_log', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_import_batch_created_at', 'import_batches', ['created_at'], unique=False)
    op.create_index('idx_import_batch_status', 'import_batches', ['status'], unique=False)

    # 2. 擴展 customers 表（新增欄位）
    op.add_column('customers', sa.Column('ad_source', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('import_batch_id', sa.String(length=36), nullable=True))
    op.create_foreign_key('fk_customer_import_batch', 'customers', 'import_batches', ['import_batch_id'], ['id'], ondelete='SET NULL')
    op.create_index('idx_ad_source', 'customers', ['ad_source'], unique=False)
    op.create_index('idx_import_batch_id', 'customers', ['import_batch_id'], unique=False)

    # 3. 創建 interactions 表
    op.create_table(
        'interactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('interaction_type', sa.Enum('DOCUMENT', 'AUDIO', 'STATUS_CHANGE', name='interactiontype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('audio_duration', sa.Integer(), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_interaction_created_at', 'interactions', ['created_at'], unique=False)
    op.create_index('idx_interaction_customer_id', 'interactions', ['customer_id'], unique=False)
    op.create_index('idx_interaction_type', 'interactions', ['interaction_type'], unique=False)

    # 4. 創建 ai_analyses 表
    op.create_table(
        'ai_analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('interaction_id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('matched_questions', sa.JSON(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('coverage_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('extracted_info', sa.JSON(), nullable=True),
        sa.Column('is_aa_customer', sa.Boolean(), nullable=True),
        sa.Column('aa_confidence', sa.Integer(), nullable=True),
        sa.Column('aa_reasons', sa.JSON(), nullable=True),
        sa.Column('aa_score', sa.Integer(), nullable=True),
        sa.Column('ai_model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interaction_id'], ['interactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_analysis_customer_id', 'ai_analyses', ['customer_id'], unique=False)
    op.create_index('idx_ai_analysis_is_aa', 'ai_analyses', ['is_aa_customer'], unique=False)

    # 5. 創建 customer_evaluations 表
    op.create_table(
        'customer_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('ai_analysis_id', sa.String(length=36), nullable=True),
        sa.Column('grade', sa.Enum('AA', 'A', 'B', 'C', name='customergrade'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('evaluation_data', sa.JSON(), nullable=False),
        sa.Column('criteria_version', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['ai_analysis_id'], ['ai_analyses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_evaluation_created_at', 'customer_evaluations', ['created_at'], unique=False)
    op.create_index('idx_evaluation_customer_id', 'customer_evaluations', ['customer_id'], unique=False)
    op.create_index('idx_evaluation_grade', 'customer_evaluations', ['grade'], unique=False)

    # 6. 創建 health_check_reports 表
    op.create_table(
        'health_check_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('evaluation_id', sa.String(length=36), nullable=True),
        sa.Column('report_title', sa.String(length=255), nullable=False),
        sa.Column('report_content', sa.JSON(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_format', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evaluation_id'], ['customer_evaluations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_report_created_at', 'health_check_reports', ['created_at'], unique=False)
    op.create_index('idx_report_customer_id', 'health_check_reports', ['customer_id'], unique=False)


def downgrade() -> None:
    # 刪除順序與創建相反，避免外鍵約束錯誤

    # 6. 刪除 health_check_reports 表
    op.drop_index('idx_report_customer_id', table_name='health_check_reports')
    op.drop_index('idx_report_created_at', table_name='health_check_reports')
    op.drop_table('health_check_reports')

    # 5. 刪除 customer_evaluations 表
    op.drop_index('idx_evaluation_grade', table_name='customer_evaluations')
    op.drop_index('idx_evaluation_customer_id', table_name='customer_evaluations')
    op.drop_index('idx_evaluation_created_at', table_name='customer_evaluations')
    op.drop_table('customer_evaluations')

    # 4. 刪除 ai_analyses 表
    op.drop_index('idx_ai_analysis_is_aa', table_name='ai_analyses')
    op.drop_index('idx_ai_analysis_customer_id', table_name='ai_analyses')
    op.drop_table('ai_analyses')

    # 3. 刪除 interactions 表
    op.drop_index('idx_interaction_type', table_name='interactions')
    op.drop_index('idx_interaction_customer_id', table_name='interactions')
    op.drop_index('idx_interaction_created_at', table_name='interactions')
    op.drop_table('interactions')

    # 2. 移除 customers 表的擴展欄位
    op.drop_index('idx_import_batch_id', table_name='customers')
    op.drop_index('idx_ad_source', table_name='customers')
    op.drop_constraint('fk_customer_import_batch', 'customers', type_='foreignkey')
    op.drop_column('customers', 'import_batch_id')
    op.drop_column('customers', 'ad_source')

    # 1. 刪除 import_batches 表
    op.drop_index('idx_import_batch_status', table_name='import_batches')
    op.drop_index('idx_import_batch_created_at', table_name='import_batches')
    op.drop_table('import_batches')

    # 刪除 Enums（如果資料庫不再使用）
    op.execute('DROP TYPE IF EXISTS importstatus')
    op.execute('DROP TYPE IF EXISTS interactiontype')
    op.execute('DROP TYPE IF EXISTS customergrade')
