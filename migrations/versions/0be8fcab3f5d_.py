"""empty message

Revision ID: 0be8fcab3f5d
Revises: 6899d1770728
Create Date: 2021-06-04 14:50:00.287167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0be8fcab3f5d'
down_revision = '6899d1770728'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('boards', sa.Column('owner', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('boards', 'owner')
    # ### end Alembic commands ###
