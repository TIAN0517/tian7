"""create game tables

Revision ID: 001
Revises: 
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_type', sa.Enum('roulette', 'baccarat', 'dragon_tiger', 'slot', name='gametype'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('total_bet', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_win', sa.Float(), nullable=False, default=0.0),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create bets table
    op.create_table(
        'bets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bet_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('odds', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create game_results table
    op.create_table(
        'game_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('result_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create roulette_games table
    op.create_table(
        'roulette_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('wheel_number', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(10), nullable=False),
        sa.Column('is_zero', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create baccarat_games table
    op.create_table(
        'baccarat_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('player_cards', sa.JSON(), nullable=False),
        sa.Column('banker_cards', sa.JSON(), nullable=False),
        sa.Column('player_score', sa.Integer(), nullable=False),
        sa.Column('banker_score', sa.Integer(), nullable=False),
        sa.Column('winner', sa.String(10), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create dragon_tiger_games table
    op.create_table(
        'dragon_tiger_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('dragon_card', sa.JSON(), nullable=False),
        sa.Column('tiger_card', sa.JSON(), nullable=False),
        sa.Column('winner', sa.String(10), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create slot_games table
    op.create_table(
        'slot_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('reels', sa.JSON(), nullable=False),
        sa.Column('paylines', sa.JSON(), nullable=False),
        sa.Column('total_win', sa.Float(), nullable=False),
        sa.Column('bonus_triggered', sa.Boolean(), nullable=False, default=False),
        sa.Column('bonus_type', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_game_sessions_user_id', 'game_sessions', ['user_id'])
    op.create_index('ix_game_sessions_game_type', 'game_sessions', ['game_type'])
    op.create_index('ix_bets_session_id', 'bets', ['session_id'])
    op.create_index('ix_bets_user_id', 'bets', ['user_id'])
    op.create_index('ix_game_results_session_id', 'game_results', ['session_id'])

def downgrade():
    # Drop tables in reverse order
    op.drop_table('slot_games')
    op.drop_table('dragon_tiger_games')
    op.drop_table('baccarat_games')
    op.drop_table('roulette_games')
    op.drop_table('game_results')
    op.drop_table('bets')
    op.drop_table('game_sessions')
    
    # Drop enum type
    op.execute('DROP TYPE gametype') 