"""empty message

Revision ID: 4b3f6f67f766
Revises: 4cf6de55be5a
Create Date: 2020-05-18 18:41:38.622879

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4b3f6f67f766'
down_revision = '4cf6de55be5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userviewconfig', sa.Column('hidden_columns', sa.String(length=300), nullable=True))
    op.drop_column('userviewconfig', 'created_by')
    op.drop_column('userviewconfig', 'updated_by')
    op.drop_column('userviewconfig', 'hiddenColumns')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userviewconfig', sa.Column('hiddenColumns', mysql.TEXT(), nullable=True))
    op.add_column('userviewconfig', sa.Column('updated_by', mysql.VARCHAR(length=300), nullable=True))
    op.add_column('userviewconfig', sa.Column('created_by', mysql.VARCHAR(length=300), nullable=True))
    op.drop_column('userviewconfig', 'hidden_columns')
    # ### end Alembic commands ###
