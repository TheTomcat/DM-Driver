"""empty message

Revision ID: 1cdd9492083a
Revises: 327e5259fec6
Create Date: 2023-10-05 12:37:42.796374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cdd9492083a'
down_revision = '327e5259fec6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('message_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_sessions_image_id_images'), 'images', ['image_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_sessions_message_id_messages'), 'messages', ['message_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_sessions_message_id_messages'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_sessions_image_id_images'), type_='foreignkey')
        batch_op.drop_column('message_id')
        batch_op.drop_column('image_id')

    # ### end Alembic commands ###
