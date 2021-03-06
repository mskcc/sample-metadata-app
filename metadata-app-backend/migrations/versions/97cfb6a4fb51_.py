"""empty message

Revision ID: 97cfb6a4fb51
Revises: 4b3f6f67f766
Create Date: 2020-05-20 15:10:02.442273

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '97cfb6a4fb51'
down_revision = '4b3f6f67f766'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sample', sa.Column('sex', sa.String(length=300), nullable=True))
    op.drop_column('sample', 'gender')
    op.add_column('sample_version', sa.Column('sex', sa.String(length=300), autoincrement=False, nullable=True))
    op.drop_column('sample_version', 'gender')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sample_version', sa.Column('gender', mysql.VARCHAR(length=300), nullable=True))
    op.drop_column('sample_version', 'sex')
    op.add_column('sample', sa.Column('gender', mysql.VARCHAR(length=300), nullable=True))
    op.drop_column('sample', 'sex')
    # ### end Alembic commands ###
