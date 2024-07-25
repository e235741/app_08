"""empty message

Revision ID: e99532df1d88
Revises: 
Create Date: 2024-07-22 00:31:48.026046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e99532df1d88'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('homework',
    sa.Column('homework_id', sa.Integer(), nullable=False),
    sa.Column('contest', sa.String(length=120), nullable=True),
    sa.Column('limit_time', sa.String(length=120), nullable=True),
    sa.Column('submission', sa.String(length=120), nullable=True),
    sa.Column('once_a_week', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('homework_id')
    )
    op.create_table('lesson',
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('homework_num', sa.Integer(), nullable=True),
    sa.Column('number_absence', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('lesson_id')
    )
    op.create_table('chart',
    sa.Column('time_id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.String(length=120), nullable=True),
    sa.Column('finish_time', sa.String(length=120), nullable=True),
    sa.Column('day_of_week', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lesson.lesson_id'], ),
    sa.PrimaryKeyConstraint('time_id')
    )
    op.create_table('lesson_homework',
    sa.Column('lesson_homework_id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.Column('homework_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['homework_id'], ['homework.homework_id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lesson.lesson_id'], ),
    sa.PrimaryKeyConstraint('lesson_homework_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lesson_homework')
    op.drop_table('chart')
    op.drop_table('lesson')
    op.drop_table('homework')
    # ### end Alembic commands ###
