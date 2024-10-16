"""Initial migration.

Revision ID: 7d998198fb83
Revises: 
Create Date: 2024-09-07 16:10:41.958030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d998198fb83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('consumption',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('week', sa.Integer(), nullable=False),
    sa.Column('meat', sa.Integer(), nullable=True),
    sa.Column('veggie', sa.Integer(), nullable=True),
    sa.Column('vegan', sa.Integer(), nullable=True),
    sa.Column('headcount', sa.Integer(), nullable=True),
    sa.Column('waste', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('consumption')
    # ### end Alembic commands ###
