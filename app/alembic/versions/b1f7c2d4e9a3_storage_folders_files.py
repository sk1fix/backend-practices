"""storage: folder_id у файлов, уникальные ограничения, timestamptz

Revision ID: b1f7c2d4e9a3
Revises: a869f73b5da1
Create Date: 2026-09-30 18:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f7c2d4e9a3'
down_revision: Union[str, Sequence[str], None] = 'a869f73b5da1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_QUOTA_BYTES = 2 * 1024 ** 3


def _to_timestamptz(table: str, column: str) -> None:
    op.alter_column(
        table,
        column,
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        postgresql_using=f"{column} AT TIME ZONE 'UTC'",
    )


def upgrade() -> None:
    """Upgrade schema."""
    # --- users: server_default для квоты и перевод времени в timestamptz
    _to_timestamptz("users", "create_date")
    op.alter_column(
        "users",
        "used_storage",
        existing_type=sa.BigInteger(),
        existing_nullable=False,
        server_default="0",
    )
    op.alter_column(
        "users",
        "storage_quota_bytes",
        existing_type=sa.BigInteger(),
        existing_nullable=False,
        server_default=str(DEFAULT_QUOTA_BYTES),
    )

    # --- folders: updated_at, уникальность пути в пределах пользователя
    _to_timestamptz("folders", "create_date")
    op.alter_column(
        "folders", "parent_folder_id", new_column_name="parent_id")
    op.add_column(
        "folders",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.alter_column("folders", "updated_at", server_default=None)

    op.create_unique_constraint(
        "uq_folders_user_path", "folders", ["user_id", "full_path"])
    op.create_index(
        "ix_folders_user_parent", "folders", ["user_id", "parent_id"])

    # --- files: принадлежность папке вместо денормализованного filepath
    _to_timestamptz("files", "create_date")
    _to_timestamptz("files", "updated_at")

    op.add_column("files", sa.Column("folder_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_files_folder_id",
        "files",
        "folders",
        ["folder_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("files", "filepath")
    op.create_unique_constraint(
        "uq_files_user_key", "files", ["user_id", "storage_key"])
    op.create_index("ix_files_user_folder", "files", ["user_id", "folder_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_files_user_folder", table_name="files")
    op.drop_constraint("uq_files_user_key", "files", type_="unique")

    op.add_column(
        "files",
        sa.Column("filepath", sa.String(), nullable=False, server_default=""),
    )
    op.alter_column("files", "filepath", server_default=None)

    op.drop_constraint("fk_files_folder_id", "files", type_="foreignkey")
    op.drop_column("files", "folder_id")

    op.drop_index("ix_folders_user_parent", table_name="folders")
    op.drop_constraint("uq_folders_user_path", "folders", type_="unique")
    op.drop_column("folders", "updated_at")
    op.alter_column(
        "folders", "parent_id", new_column_name="parent_folder_id")

    for table, column in (
            ("files", "updated_at"),
            ("files", "create_date"),
            ("folders", "create_date"),
            ("users", "create_date"),
    ):
        op.alter_column(
            table,
            column,
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
            postgresql_using=f"{column} AT TIME ZONE 'UTC'",
        )

    op.alter_column(
        "users", "used_storage",
        existing_type=sa.BigInteger(), existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "users", "storage_quota_bytes",
        existing_type=sa.BigInteger(), existing_nullable=False,
        server_default=None,
    )
