"""Initial migration

Revision ID: 8855f8d400c3
Revises:
Create Date: 2024-11-02 18:00:24.634465

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8855f8d400c3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "additive",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tri_chemical_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="unique_name"),
        sa.UniqueConstraint("tri_chemical_id", name="unique_tri_chemical_id"),
    )
    op.create_table(
        "chemical_activity",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("parent_chemical_activity_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_chemical_activity_id"],
            ["chemical_activity.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="unique_activity_name"),
    )
    op.create_table(
        "consumer_commercial_function_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", name="unique_function_category"),
    )
    op.create_table(
        "consumer_commercial_product_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", name="unique_product_category"),
    )
    op.create_table(
        "end_of_life_activity",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("management_type", sa.String(), nullable=False),
        sa.Column("is_on_site", sa.Boolean(), nullable=False),
        sa.Column("is_hazardous_waste", sa.Boolean(), nullable=False),
        sa.Column("is_metal", sa.Boolean(), nullable=False),
        sa.Column("is_wastewater", sa.Boolean(), nullable=False),
        sa.Column("is_recycling", sa.Boolean(), nullable=False),
        sa.Column("is_landfilling", sa.Boolean(), nullable=False),
        sa.Column("is_potw", sa.Boolean(), nullable=False),
        sa.Column("is_incineration", sa.Boolean(), nullable=False),
        sa.Column("is_brokering", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="unique_end_of_life_name"),
    )
    op.create_table(
        "industrial_type_of_process_or_use",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", name="unique_process_or_use"),
    )
    op.create_table(
        "industry_function_category",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("name", name="unique_industry_function_category"),
    )
    op.create_table(
        "industry_sector",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("naics_code", sa.String(), nullable=False),
        sa.Column("naics_title", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("naics_code", name="unique_naics_code"),
    )
    op.create_table(
        "industry_use_sector",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("code", name="unique_industry_sector_code"),
    )
    op.create_table(
        "release_type",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_on_site", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="unique_release_type_name"),
    )
    op.create_table(
        "consumer_commercial_use",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("additive_id", sa.Integer(), nullable=False),
        sa.Column("industry_sector_id", sa.Integer(), nullable=False),
        sa.Column("product_category_id", sa.Integer(), nullable=True),
        sa.Column("function_category_id", sa.Integer(), nullable=True),
        sa.Column("type_of_use", sa.String(), nullable=True),
        sa.Column("percentage", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["additive_id"],
            ["additive.id"],
        ),
        sa.ForeignKeyConstraint(
            ["function_category_id"],
            ["consumer_commercial_function_category.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industry_sector_id"],
            ["industry_sector.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_category_id"],
            ["consumer_commercial_product_category.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "industrial_use",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("additive_id", sa.Integer(), nullable=False),
        sa.Column("industrial_type_of_process_or_use_id", sa.Integer(), nullable=True),
        sa.Column("industry_function_category_id", sa.Integer(), nullable=True),
        sa.Column("percentage", sa.Float(), nullable=True),
        sa.Column("industry_use_sector_id", sa.Integer(), nullable=True),
        sa.Column("industry_sector_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["additive_id"],
            ["additive.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industrial_type_of_process_or_use_id"],
            ["industrial_type_of_process_or_use.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industry_function_category_id"],
            ["industry_function_category.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industry_sector_id"],
            ["industry_sector.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industry_use_sector_id"],
            ["industry_use_sector.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "industry_use_sector_naics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("naics_code_2007", sa.String(), nullable=False),
        sa.Column("industry_use_sector_id", sa.Integer(), nullable=False),
        sa.Column("naics_code_2012", sa.String(), nullable=True),
        sa.Column("naics_code_2017", sa.String(), nullable=True),
        sa.Column("naics_code_2022", sa.String(), nullable=True),
        sa.Column("industry_sector_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["industry_sector_id"],
            ["industry_sector.id"],
        ),
        sa.ForeignKeyConstraint(
            ["industry_use_sector_id"],
            ["industry_use_sector.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("naics_code_2007", name="unique_naics_code_2007"),
    )
    op.create_table(
        "record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("additive_id", sa.Integer(), nullable=False),
        sa.Column("waste_generator_industry_sector_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("end_of_life_activity_id", sa.Integer(), nullable=True),
        sa.Column("release_type_id", sa.Integer(), nullable=True),
        sa.Column("waste_handler_industry_sector_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["additive_id"],
            ["additive.id"],
        ),
        sa.ForeignKeyConstraint(
            ["end_of_life_activity_id"],
            ["end_of_life_activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["release_type_id"],
            ["release_type.id"],
        ),
        sa.ForeignKeyConstraint(
            ["waste_generator_industry_sector_id"],
            ["industry_sector.id"],
        ),
        sa.ForeignKeyConstraint(
            ["waste_handler_industry_sector_id"],
            ["industry_sector.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "record_chemical_activity",
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("chemical_activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chemical_activity_id"],
            ["chemical_activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["record.id"],
        ),
        sa.PrimaryKeyConstraint("record_id", "chemical_activity_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("record_chemical_activity")
    op.drop_table("record")
    op.drop_table("industry_use_sector_naics")
    op.drop_table("industrial_use")
    op.drop_table("consumer_commercial_use")
    op.drop_table("release_type")
    op.drop_table("industry_use_sector")
    op.drop_table("industry_sector")
    op.drop_table("industry_function_category")
    op.drop_table("industrial_type_of_process_or_use")
    op.drop_table("end_of_life_activity")
    op.drop_table("consumer_commercial_product_category")
    op.drop_table("consumer_commercial_function_category")
    op.drop_table("chemical_activity")
    op.drop_table("additive")
    # ### end Alembic commands ###
