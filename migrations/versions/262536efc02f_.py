"""empty message

Revision ID: 262536efc02f
Revises: 8fc0b9bf7a00
Create Date: 2019-12-10 11:25:27.669483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '262536efc02f'
down_revision = '8fc0b9bf7a00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('carts', sa.Column('checkout', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('carts', 'checkout')
    # ### end Alembic commands ###