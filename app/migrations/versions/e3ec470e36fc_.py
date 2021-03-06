"""empty message

Revision ID: e3ec470e36fc
Revises: 65bd590f11a2
Create Date: 2018-04-18 14:46:53.858328

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e3ec470e36fc'
down_revision = '65bd590f11a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('discount', sa.Float(), nullable=True))
    op.add_column('product', sa.Column('isKilled', sa.Boolean(), nullable=True))
    op.drop_column('product', 'old_price')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('old_price', mysql.FLOAT(), nullable=True))
    op.drop_column('product', 'isKilled')
    op.drop_column('product', 'discount')
    # ### end Alembic commands ###
