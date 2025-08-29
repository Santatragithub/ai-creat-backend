"""init schema

Revision ID: 6286f5cd5c5b
Revises: None
Create Date: 2025-08-29 08:32:56.021454+00:00

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6286f5cd5c5b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    user_role = postgresql.ENUM("user", "admin", name="user_role")
    project_status = postgresql.ENUM(
        "uploading", "processing", "ready_for_review", "generating", "completed", "failed", name="project_status"
    )
    job_status = postgresql.ENUM("pending", "processing", "completed", "failed", name="job_status")
    format_type = postgresql.ENUM("resizing", "repurposing", name="format_type")

    user_role.create(op.get_bind(), checkfirst=True)
    project_status.create(op.get_bind(), checkfirst=True)
    job_status.create(op.get_bind(), checkfirst=True)
    format_type.create(op.get_bind(), checkfirst=True)

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(255), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="user"),
        sa.Column("preferences", sa.dialects.postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # projects
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", project_status, nullable=False, server_default="uploading"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # assets
    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("dimensions", sa.dialects.postgresql.JSONB()),
        sa.Column("dpi", sa.Integer()),
        sa.Column("ai_metadata", sa.dialects.postgresql.JSONB()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # generation_jobs
    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.UUID(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", job_status, nullable=False, server_default="pending"),
        sa.Column("progress", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # repurposing_platforms
    op.create_table(
        "repurposing_platforms",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_by_admin_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # asset_formats
    op.create_table(
        "asset_formats",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", format_type, nullable=False),
        sa.Column("platform_id", sa.UUID(), sa.ForeignKey("repurposing_platforms.id", ondelete="CASCADE")),
        sa.Column("category", sa.String(50)),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_by_admin_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # generated_assets
    op.create_table(
        "generated_assets",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", sa.UUID(), sa.ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_asset_id", sa.UUID(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_format_id", sa.UUID(), sa.ForeignKey("asset_formats.id", ondelete="SET NULL")),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("dimensions", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("is_nsfw", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("manual_edits", sa.dialects.postgresql.JSONB()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # text_style_sets
    op.create_table(
        "text_style_sets",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("styles", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_by_admin_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # app_settings
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rule_key", sa.String(255), unique=True, nullable=False),
        sa.Column("rule_value", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Indexes
    op.create_index("idx_projects_user_id", "projects", ["user_id"])
    op.create_index("idx_assets_project_id", "assets", ["project_id"])
    op.create_index("idx_generated_assets_job_id", "generated_assets", ["job_id"])
    op.create_index("idx_asset_formats_type", "asset_formats", ["type"])


def downgrade() -> None:
    op.drop_index("idx_asset_formats_type", table_name="asset_formats")
    op.drop_index("idx_generated_assets_job_id", table_name="generated_assets")
    op.drop_index("idx_assets_project_id", table_name="assets")
    op.drop_index("idx_projects_user_id", table_name="projects")

    op.drop_table("app_settings")
    op.drop_table("text_style_sets")
    op.drop_table("generated_assets")
    op.drop_table("asset_formats")
    op.drop_table("repurposing_platforms")
    op.drop_table("generation_jobs")
    op.drop_table("assets")
    op.drop_table("projects")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS format_type CASCADE")
    op.execute("DROP TYPE IF EXISTS job_status CASCADE")
    op.execute("DROP TYPE IF EXISTS project_status CASCADE")
    op.execute("DROP TYPE IF EXISTS user_role CASCADE")
