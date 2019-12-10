"""empty message

Revision ID: c59a76d6cd7c
Revises: 
Create Date: 2019-12-07 03:11:38.024660

"""
from alembic import op
import sqlalchemy as sa ,sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'c59a76d6cd7c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('seller', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'product', 'users', ['seller'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.drop_column('product', 'seller')
    # ### end Alembic commands ###