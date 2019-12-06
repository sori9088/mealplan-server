"""empty message

Revision ID: 5e261b992846
Revises: 
Create Date: 2019-12-06 16:32:37.721357

"""
from alembic import op
import sqlalchemy as sa,sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '5e261b992846'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('email', sa.String(length=80), nullable=True),
    sa.Column('password', sa.String(length=200), nullable=True),
    sa.Column('avatar_url', sa.String(), nullable=True),
    sa.Column('seller', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('flask_dance_oauth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('token', sqlalchemy_utils.types.json.JSONType(), nullable=False),
    sa.Column('provider_user_id', sa.String(length=256), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider_user_id')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('img_url', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('price', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token')
    op.drop_table('product')
    op.drop_table('flask_dance_oauth')
    op.drop_table('users')
    # ### end Alembic commands ###
