# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Data models module.

This module defines SQLAlchemy models for a database schema supporting the
tracking of chemical activities, industry sectors, and records of chemical
additives, along with their various end-of-life and release activities.

Classes and Tables:

    - Additive: Represents a chemical additive with a name and TRI chemical ID.
    - IndustrySector: Stores information about industry sectors, including NAICS
    code and title.
    - ChemicalActivity: Describes activities related to chemicals, including
    a self-referential relationship for hierarchical parent-child relationships.
    - EndOfLifeActivity: Stores details on activities related to the end-of-life
    processing of chemicals, with attributes such as management_type, is_on_site,
    and flags indicating if the activity involves hazardous waste, metals, or recycling.
    - ReleaseType: Represents types of release activities (e.g., fugitive, stack),
    with an attribute is_on_site to indicate the location of the release.
    - Record: Tracks records of chemical activities and releases by connecting
    Additive, IndustrySector, EndOfLifeActivity, and ReleaseType entries.
    It uses nullable foreign keys for end_of_life_activity and release_type,
    allowing records to reference either but not both, and includes a many-to-many
    relationship with ChemicalActivity through the association table
    record_chemical_activity.
    - record_chemical_activity (Association Table): Supports the many-to-many
    relationship between Record and ChemicalActivity, allowing each record to
    link to multiple chemical activities and vice versa.

Key Features:

    - Hierarchical Relationships: ChemicalActivity supports hierarchical
    structures with a self-referential parent-child relationship.
    - Conditional Foreign Keys: Record uses nullable fields for end_of_life_activity
    and release_type to enforce that a record can reference either, but not both.
    - Many-to-Many Association: The many-to-many relationship between Record
    and ChemicalActivity is implemented via the record_chemical_activity table.
    - Detailed End-of-Life Attributes: EndOfLifeActivity includes various
    boolean fields to categorize types of activities such as is_recycling and
    is_incineration, facilitating detailed tracking of chemical disposition.

This module provides a foundation for tracking chemical additives across industry
sectors, documenting their release and end-of-life handling with detailed
categorization, supporting comprehensive data logging and retrieval.

"""


from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association Table for many-to-many relationship between Record and ChemicalActivity
record_chemical_activity = Table(
    "record_chemical_activity",
    Base.metadata,
    Column(
        "record_id",
        ForeignKey("record.id"),
        primary_key=True,
    ),
    Column(
        "chemical_activity_id",
        ForeignKey("chemical_activity.id"),
        primary_key=True,
    ),
)


class Additive(Base):
    """Represents a chemical additive with a name and TRI chemical ID."""

    __tablename__ = "additive"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    tri_chemical_id = Column(
        String,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("tri_chemical_id", name="unique_tri_chemical_id"),
        UniqueConstraint("name", name="unique_name"),
    )

    def __repr__(self):
        return f"<Additive(name={self.name}, tri_chemical_id={self.tri_chemical_id})>"


class ConsumerCommercialProductCategory(Base):
    """Represents consumer/commercial product categories."""

    __tablename__ = "consumer_commercial_product_category"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="unique_product_category",
        ),
    )

    def __repr__(self):
        return f"<ConsumerCommercialProductCategory(name={self.name})>"


class ConsumerCommercialFunctionCategory(Base):
    """Represents consumer/commercial function categories."""

    __tablename__ = "consumer_commercial_function_category"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    __table_args__ = (UniqueConstraint("name", name="unique_function_category"),)

    def __repr__(self):
        return f"<ConsumerCommercialFunctionCategory(name={self.name})>"


class IndustryFunctionCategory(Base):
    """Represents industry function categories."""

    __tablename__ = "industry_function_category"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    __table_args__ = (UniqueConstraint("name", name="unique_industry_function_category"),)

    def __repr__(self):
        return f"<IndustryFunctionCategory(name={self.name})>"


class IndustrialTypeOfProcessOrUse(Base):
    """Represents industrial types of processes or uses."""

    __tablename__ = "industrial_type_of_process_or_use"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    __table_args__ = (UniqueConstraint("name", name="unique_process_or_use"),)

    def __repr__(self):
        return f"<IndustrialTypeOfProcessOrUse(name={self.name})>"


class IndustrySector(Base):
    """Stores information about industry sectors, including NAICS code and title."""

    __tablename__ = "industry_sector"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    naics_code = Column(
        String,
        nullable=False,
    )
    naics_title = Column(
        String,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "naics_code",
            "naics_title",
            name="unique_column_code_title",
        ),
    )

    def __repr__(self):
        return f"<IndustrySector(naics_code={self.naics_code}, naics_title={self.naics_title})>"


class IndustryUseSector(Base):
    """Represents the industry use sector for CRD industrial processing and use."""

    __tablename__ = "industry_use_sector"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    code = Column(
        String,
        nullable=False,
        unique=True,
    )
    name = Column(
        String,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="unique_industry_sector_code",
        ),
    )

    def __repr__(self):
        return f"<IndustryUseSector(code={self.code}, name={self.name})>"


class IndustryUseSectorNaics(Base):
    """Represents the NAICS entries for industry use sectors."""

    __tablename__ = "industry_use_sector_naics"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    industry_use_sector_id = Column(
        Integer,
        ForeignKey("industry_use_sector.id"),
        nullable=False,
    )
    industry_sector_id = Column(
        Integer,
        ForeignKey("industry_sector.id"),
        nullable=True,
    )

    # Relationships
    industry_sector = relationship("IndustryUseSector", backref="naics_entries")
    industry_sector_ref = relationship("IndustrySector", backref="naics_links")

    def __repr__(self):
        return f"<IndustryUseSectorNaics(industry_use_sector_id={self.industry_use_sector_id}, industry_sector_id={self.industry_sector_id})>"


class ChemicalActivity(Base):
    """Describes activities related to chemicals, including hierarchical parent-child relationships."""

    __tablename__ = "chemical_activity"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    description = Column(
        String,
        nullable=True,
    )
    parent_chemical_activity_id = Column(
        Integer,
        ForeignKey("chemical_activity.id"),
        nullable=True,
    )

    # Self-referential relationship for parent activity
    parent_activity = relationship(
        "ChemicalActivity",
        remote_side=[id],
        backref="sub_activities",
    )

    __table_args__ = (UniqueConstraint("name", name="unique_activity_name"),)

    def __repr__(self):
        return f"<ChemicalActivity(name={self.name}, description={self.description})>"


class EndOfLifeActivity(Base):
    """Stores details on activities related to the end-of-life processing of chemicals."""

    __tablename__ = "end_of_life_activity"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    management_type = Column(
        String,
        nullable=False,
    )
    is_on_site = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_hazardous_waste = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_metal = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_wastewater = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_recycling = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_landfilling = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_potw = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_incineration = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_brokering = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="unique_end_of_life_name",
        ),
    )

    def __repr__(self):
        return f"<EndOfLifeActivity(name={self.name}, management_type={self.management_type})>"


class ReleaseType(Base):
    """Represents types of release activities (e.g., fugitive, stack)."""

    __tablename__ = "release_type"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(
        String,
        nullable=False,
    )
    is_on_site = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="unique_release_type_name",
        ),
    )

    def __repr__(self):
        return f"<ReleaseType(name={self.name}, is_on_site={self.is_on_site})>"


class Record(Base):
    """Tracks records of chemical activities and releases."""

    __tablename__ = "record"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    trifid = Column(
        String,
        nullable=False,
    )
    additive_id = Column(
        Integer,
        ForeignKey("additive.id"),
        nullable=False,
    )
    waste_generator_industry_sector_id = Column(
        Integer,
        ForeignKey("industry_sector.id"),
        nullable=False,
    )
    amount = Column(
        Float,
        nullable=False,
    )
    end_of_life_activity_id = Column(
        Integer,
        ForeignKey("end_of_life_activity.id"),
        nullable=True,
    )
    release_type_id = Column(
        Integer,
        ForeignKey("release_type.id"),
        nullable=True,
    )
    waste_handler_industry_sector_id = Column(
        Integer,
        ForeignKey("industry_sector.id"),
        nullable=True,
    )

    # Relationships
    additive = relationship(
        "Additive",
        backref="records",
    )
    waste_generator_industry_sector = relationship(
        "IndustrySector",
        foreign_keys=[waste_generator_industry_sector_id],
        backref="generator_records",
    )
    end_of_life_activity = relationship(
        "EndOfLifeActivity",
        backref="records",
    )
    release_type = relationship(
        "ReleaseType",
        backref="records",
    )
    chemical_activities = relationship(
        "ChemicalActivity",
        secondary=record_chemical_activity,
        backref="records",
    )
    waste_handler_industry_sector = relationship(
        "IndustrySector",
        foreign_keys=[waste_handler_industry_sector_id],
        backref="handler_records",
    )

    def __repr__(self):
        return f"<Record(amount={self.amount}, additive_id={self.additive_id})>"


class ConsumerCommercialUse(Base):
    """Represents consumer and commercial use records in CDR."""

    __tablename__ = "consumer_commercial_use"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    additive_id = Column(
        Integer,
        ForeignKey("additive.id"),
        nullable=False,
    )
    industry_sector_id = Column(
        Integer,
        ForeignKey("industry_sector.id"),
        nullable=True,
    )
    product_category_id = Column(
        Integer,
        ForeignKey("consumer_commercial_product_category.id"),
        nullable=True,
    )
    function_category_id = Column(
        Integer,
        ForeignKey("consumer_commercial_function_category.id"),
        nullable=True,
    )
    type_of_use = Column(
        String,
        nullable=True,
    )
    percentage = Column(
        Float,
        nullable=True,
    )

    additive = relationship("Additive", backref="consumer_commercial_uses")
    product_category = relationship("ConsumerCommercialProductCategory", backref="uses")
    function_category = relationship("ConsumerCommercialFunctionCategory", backref="uses")
    industry_sector = relationship("IndustrySector", backref="consumer_commercial_uses")

    def __repr__(self):
        return f"<ConsumerCommercialUse(additive_id={self.additive_id}, naics_code={self.naics_code})>"


class IndustrialUse(Base):
    """Represents industrial use records."""

    __tablename__ = "industrial_use"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    additive_id = Column(
        Integer,
        ForeignKey("additive.id"),
        nullable=False,
    )
    industrial_type_of_process_or_use_id = Column(
        Integer,
        ForeignKey("industrial_type_of_process_or_use.id"),
        nullable=True,
    )
    industry_function_category_id = Column(
        Integer,
        ForeignKey("industry_function_category.id"),
        nullable=True,
    )
    percentage = Column(
        Float,
        nullable=True,
    )
    industry_use_sector_id = Column(
        Integer,
        ForeignKey("industry_use_sector.id"),
        nullable=True,
    )
    industry_sector_id = Column(
        Integer,
        ForeignKey("industry_sector.id"),
        nullable=True,
    )

    additive = relationship(
        "Additive",
        backref="industrial_uses",
    )
    industrial_type = relationship(
        "IndustrialTypeOfProcessOrUse",
        backref="uses",
    )
    function_category = relationship(
        "IndustryFunctionCategory",
        backref="uses",
    )
    industry_use_sector = relationship(
        "IndustryUseSector",
        backref="industrial_uses",
    )
    industry_sector = relationship(
        "IndustrySector",
        backref="industrial_uses",
    )

    def __repr__(self):
        return f"<IndustrialUse(additive_id={self.additive_id}, naics_code={self.naics_code})>"
