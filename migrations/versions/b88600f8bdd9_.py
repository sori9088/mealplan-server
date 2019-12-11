"""empty message

Revision ID: b88600f8bdd9
Revises: f2fe2dc17f80
Create Date: 2019-12-10 18:08:08.987049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b88600f8bdd9'
down_revision = 'f2fe2dc17f80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('price', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'price')
    # ### end Alembic commands ###