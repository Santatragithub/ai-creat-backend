"""init schema

Revision ID: 3f2a1c8f1b6a
Revises: 
Create Date: 2025-08-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "3f2a1c8f1b6a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Ensure gen_random_uuid() is available
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    user_role = postgresql.ENUM("user", "admin", name="user_role")
    user_role.create(op.get_bind())

    project_status = postgresql.ENUM(
        "uploading", "processing", "ready_for_review", "generating", "completed", "failed", name="project_status"
    )
    project_status.create(op.get_bind())

    job_status = postgresql.ENUM("pending", "processing", "completed", "failed", name="job_status")
    job_status.create(op.get_bind())

    format_type = postgresql.ENUM("resizing", "repurposing", name="format_type")
    format_type.create(op.get_bind())

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(255), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("role", sa.Enum("user", "admin", name="user_role"), nullable=False, server_default="user"),
        sa.Column("preferences", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "uploading",
                "processing",
                "ready_for_review",
                "generating",
                "completed",
                "failed",
                name="project_status",
            ),
            nullable=False,
            server_default="uploading",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("dimensions", postgresql.JSONB),
        sa.Column("dpi", sa.Integer()),
        sa.Column("ai_metadata", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "generation_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="job_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("progress", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "repurposing_platforms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by_admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "asset_formats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.Enum("resizing", "repurposing", name="format_type"), nullable=False),
        sa.Column(
            "platform_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("repurposing_platforms.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("category", sa.String(50)),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by_admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "generated_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "asset_format_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("asset_formats.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("dimensions", postgresql.JSONB, nullable=False),
        sa.Column("is_nsfw", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("manual_edits", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "text_style_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("styles", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by_admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("rule_key", sa.String(255), unique=True, nullable=False),
        sa.Column("rule_value", postgresql.JSONB, nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("idx_projects_user_id", "projects", ["user_id"])
    op.create_index("idx_assets_project_id", "assets", ["project_id"])
    op.create_index("idx_generated_assets_job_id", "generated_assets", ["job_id"])
    op.create_index("idx_asset_formats_type", "asset_formats", ["type"])


def downgrade():
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

    # Drop ENUMs explicitly using the same dialect enum helper
    user_role = postgresql.ENUM(name="user_role")
    project_status = postgresql.ENUM(name="project_status")
    job_status = postgresql.ENUM(name="job_status")
    format_type = postgresql.ENUM(name="format_type")

    user_role.drop(op.get_bind(), checkfirst=True)
    project_status.drop(op.get_bind(), checkfirst=True)
    job_status.drop(op.get_bind(), checkfirst=True)
    format_type.drop(op.get_bind(), checkfirst=True)
