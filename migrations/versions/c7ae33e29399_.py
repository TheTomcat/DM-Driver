"""empty message

Revision ID: c7ae33e29399
Revises: 
Create Date: 2023-10-04 22:02:28.827913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7ae33e29399'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_images'))
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=400), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tags'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags')
    op.drop_table('messages')
    op.drop_table('images')
    # ### end Alembic commands ###