"""empty message

Revision ID: 1da212a10f5d
Revises: 7422632de568
Create Date: 2023-10-29 00:23:08.203986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1da212a10f5d'
down_revision = '7422632de568'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('initiative_modifier', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.drop_column('initiative_modifier')

    # ### end Alembic commands ###
