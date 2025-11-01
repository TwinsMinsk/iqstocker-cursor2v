"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade migration - создание всех таблиц"""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('subscription_tier', sa.String(length=50), nullable=False),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('referrer_id', sa.Integer(), nullable=True),
        sa.Column('iq_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], ),
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)
    op.create_index('ix_users_subscription_expires_at', 'users', ['subscription_expires_at'], unique=False)
    op.create_index('ix_users_referrer_id', 'users', ['referrer_id'], unique=False)
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)
    
    # Create limits table
    op.create_table(
        'limits',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analytics_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('analytics_limit', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('themes_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('themes_limit', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('reset_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create csv_analyses table
    op.create_table(
        'csv_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False),
        sa.Column('analysis_status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_csv_analyses_user_id', 'csv_analyses', ['user_id'], unique=False)
    op.create_index('ix_csv_analyses_created_at', 'csv_analyses', ['created_at'], unique=False)
    
    # Create analytics_reports table
    op.create_table(
        'analytics_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('csv_analysis_id', sa.Integer(), nullable=False),
        sa.Column('kpi_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['csv_analysis_id'], ['csv_analyses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_analytics_reports_csv_analysis_id', 'analytics_reports', ['csv_analysis_id'], unique=True)
    
    # Create theme_templates table
    op.create_table(
        'theme_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('theme', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_theme_templates_category', 'theme_templates', ['category'], unique=False)
    op.create_index('ix_theme_templates_is_active', 'theme_templates', ['is_active'], unique=False)
    
    # Create theme_requests table
    op.create_table(
        'theme_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_theme_requests_user_id', 'theme_requests', ['user_id'], unique=False)
    op.create_index('ix_theme_requests_created_at', 'theme_requests', ['created_at'], unique=False)
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tribute_transaction_id', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='RUB'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('subscription_tier', sa.String(length=50), nullable=False),
        sa.Column('subscription_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('payment_provider', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_payments_user_id', 'payments', ['user_id'], unique=False)
    op.create_index('ix_payments_created_at', 'payments', ['created_at'], unique=False)
    op.create_index('ix_payments_tribute_transaction_id', 'payments', ['tribute_transaction_id'], unique=True)
    
    # Create system_messages table
    op.create_table(
        'system_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create broadcast_messages table
    op.create_table(
        'broadcast_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('target_subscription', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Downgrade migration - удаление всех таблиц"""
    
    op.drop_table('broadcast_messages')
    op.drop_table('system_messages')
    op.drop_index('ix_payments_tribute_transaction_id', table_name='payments')
    op.drop_index('ix_payments_created_at', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_table('payments')
    op.drop_index('ix_theme_requests_created_at', table_name='theme_requests')
    op.drop_index('ix_theme_requests_user_id', table_name='theme_requests')
    op.drop_table('theme_requests')
    op.drop_index('ix_theme_templates_is_active', table_name='theme_templates')
    op.drop_index('ix_theme_templates_category', table_name='theme_templates')
    op.drop_table('theme_templates')
    op.drop_index('ix_analytics_reports_csv_analysis_id', table_name='analytics_reports')
    op.drop_table('analytics_reports')
    op.drop_index('ix_csv_analyses_created_at', table_name='csv_analyses')
    op.drop_index('ix_csv_analyses_user_id', table_name='csv_analyses')
    op.drop_table('csv_analyses')
    op.drop_table('limits')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_referrer_id', table_name='users')
    op.drop_index('ix_users_subscription_expires_at', table_name='users')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')

