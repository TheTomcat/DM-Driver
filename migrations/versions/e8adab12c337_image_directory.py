"""image directory

Revision ID: e8adab12c337
Revises: cff6ff213e74
Create Date: 2023-10-27 14:39:00.986447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8adab12c337"
down_revision = "cff6ff213e74"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "directories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_directories")),
    )
    with op.batch_alter_table("directories", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_directories_path"), ["path"], unique=True)

    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("directory_id", sa.Integer(), nullable=False, default="")
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_images_directory_id_directories"),
            "directories",
            ["directory_id"],
            ["id"],
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_images_directory_id_directories"), type_="foreignkey"
        )
        batch_op.drop_column("directory_id")

    with op.batch_alter_table("directories", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_directories_path"))

    op.drop_table("directories")
    # ### end Alembic commands ###
