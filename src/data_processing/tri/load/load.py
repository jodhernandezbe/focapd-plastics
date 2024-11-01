# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Load data into database."""

from typing import Optional, Tuple

import pandas as pd
from omegaconf import DictConfig
from sqlalchemy import Column
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.data_processing.data_models import (
    Additive,
    ChemicalActivity,
    EndOfLifeActivity,
    IndustrySector,
    Record,
    ReleaseType,
    record_chemical_activity,
)


class TriDataLoader:
    """Class for loading data into the TRI database.

    Attributes:
        config (DictConfig): The configuration object.
        session (Session): The database session object.

    """

    def __init__(
        self,
        config: DictConfig,
        session: Session,
    ):
        self.config = config
        self.session = session
        self._df_1b_filtered: pd.DataFrame

    def element_exists(self, model, **kwargs):
        """Check if an element exists in the database."""
        try:
            self.session.query(model).filter_by(**kwargs).one()
            return True
        except NoResultFound:
            return False

    def get_or_create(self, model, **kwargs):
        """Get an element if it exists, otherwise create it."""
        try:
            element = self.session.query(model).filter_by(**kwargs).one()
        except NoResultFound:
            element = self.create_element(model, **kwargs)
        return element

    def create_element(self, model, **kwargs):
        """Create an element in the database."""
        element = model(**kwargs)
        self.session.add(element)
        self.session.commit()
        return element

    def load_chemical_activity(self):
        """Load chemical activities into the database."""
        chemical_activities = [col for col in self.config.tri_files.file_1b.needed_columns if "is_general_info" not in col]

        for activity in chemical_activities:
            if (dependency_name := activity.get("depends_on")) is not None:
                dependency = self.get_or_create(
                    ChemicalActivity,
                    name=dependency_name,
                )
                dependency_id = dependency.id if dependency else None
            else:
                dependency_id = None

            if not self.element_exists(
                ChemicalActivity,
                name=activity["name"],
            ):
                self.create_element(
                    ChemicalActivity,
                    name=activity["name"],
                    description=activity.get("description", None),
                    parent_chemical_activity_id=dependency_id,
                )

    def load_plastic_additives(self):
        """Load plastic additives into the database."""
        plastic_additives = self.config.plastic_additives.tri_chem_id

        for additive in plastic_additives:
            if not self.element_exists(
                Additive,
                tri_chemical_id=additive["CASRN"],
            ):
                self.create_element(
                    Additive,
                    name=additive["name"],
                    tri_chemical_id=additive["CASRN"],
                )

    def load_release_management_type(
        self,
        df: pd.DataFrame,
        table_name: str,
    ):
        """Load release and management types into the database.

        Args:
            df (pd.DataFrame): The DataFrame containing the release types.
            table_name (str): The name of the table in the database.

        """
        df.to_sql(
            table_name,
            self.session.get_bind(),
            if_exists="append",
            index=False,
        )

    @property
    def df_1b_filtered(self) -> pd.DataFrame:
        """Return the filtered 1b DataFrame."""
        if not hasattr(self, "_df_1b_filtered"):
            if self._df_1b is None:
                raise ValueError("1b DataFrame not set.")
            self._df_1b_filtered = self._df_1b[self._df_1b["is_performed"] == "Yes"]
        return self._df_1b_filtered

    def merge_with_1b(
        self,
        df_main: pd.DataFrame,
    ) -> pd.DataFrame:
        """Merge main DataFrame with filtered 1b data on 'trifid' and filter for 'is_performed' == 'Yes'."""
        # Merge main DataFrame with filtered 1b on 'trifid'
        df_enriched = df_main.merge(
            self.df_1b_filtered[
                [
                    "trifid",
                    "tri_chem_id",
                    "naics_code",
                    "naics_title",
                    "chemical_activity",
                ]
            ],
            on=["trifid", "tri_chem_id"],
            how="left",  # Keep all rows in the main DataFrame
        )
        return df_enriched

    def load_records(
        self,
        df: pd.DataFrame,
        record_type: str,
        handler_columns: Optional[Tuple[str, str]] = None,
    ):
        """Load records into the Record table based on enriched DataFrame and type."""
        for _, row in df.iterrows():

            if not pd.notnull(row["naics_code"]):
                continue

            # Map additive_id using tri_chem_id
            additive_id = self._get_or_create_additive(row["tri_chem_id"])

            # Get waste generator industry sector id
            waste_generator_industry_sector_id = self._get_waste_generator_industry_sector_id(row)

            # Get waste handler industry sector id if handler_columns are provided
            waste_handler_industry_sector_id = self._get_waste_handler_industry_sector_id(row, handler_columns)

            # Determine end_of_life_activity_id or release_type_id based on record_type
            end_of_life_activity_id = self._get_end_of_life_activity_id(row) if record_type == "management" else None
            release_type_id = self._get_release_type_id(row) if record_type == "release" else None

            # Create Record instance
            record = Record(
                additive_id=additive_id,
                waste_generator_industry_sector_id=waste_generator_industry_sector_id,
                amount=row.get("amount", 0.0),
                end_of_life_activity_id=end_of_life_activity_id,
                release_type_id=release_type_id,
                waste_handler_industry_sector_id=waste_handler_industry_sector_id,
            )
            self.session.add(record)
            self.session.flush()  # Ensures `record.id` is available for `record_chemical_activity`

            # Associate chemical activity with record
            self._associate_chemical_activity(record.id, row)

        # Commit after all records are added
        self.session.commit()

    def _get_or_create_additive(
        self,
        tri_chem_id: str,
    ):
        """Fetch or create an Additive and return its id."""
        additive = self.get_or_create(
            Additive,
            tri_chemical_id=tri_chem_id,
        )
        return additive.id

    def _get_waste_generator_industry_sector_id(
        self,
        row: pd.Series,
    ):
        """Fetch or create IndustrySector for the waste generator and return its id."""
        if "naics_code" in row and not pd.isnull(row["naics_code"]):
            sector = self.get_or_create(
                IndustrySector,
                naics_code=row["naics_code"],
                naics_title=row["naics_title"],
            )
            return sector.id
        return None

    def _get_waste_handler_industry_sector_id(
        self,
        row: pd.Series,
        handler_columns: Optional[Tuple[str, str]],
    ):
        """Fetch or create IndustrySector for the waste handler and return its id."""
        if handler_columns:
            naics_code_col, naics_title_col = handler_columns
            if naics_code_col in row and not pd.isnull(row[naics_code_col]):
                sector = self.get_or_create(
                    IndustrySector,
                    naics_code=row[naics_code_col],
                    naics_title=row[naics_title_col],
                )
                return sector.id
        return None

    def _get_end_of_life_activity_id(
        self,
        row: pd.Series,
    ):
        """Fetch or create EndOfLifeActivity and return its id if record_type is management."""
        if "eol_name" in row:
            activity = self.session.query(EndOfLifeActivity).filter_by(name=row["eol_name"]).one()
            return activity.id
        return None

    def _get_release_type_id(
        self,
        row: pd.Series,
    ):
        """Fetch or create ReleaseType and return its id if record_type is release."""
        if "eol_name" in row:
            release_type = self.session.query(ReleaseType).filter_by(name=row["eol_name"]).one()
            return release_type.id
        return None

    def _associate_chemical_activity(
        self,
        record_id: Column[int],
        row: pd.Series,
    ):
        """Associate a chemical activity with the given record."""
        if "chemical_activity" in row and pd.notnull(row["chemical_activity"]):
            chemical_activity = self.get_or_create(
                ChemicalActivity,
                name=row["chemical_activity"],
            )
            self.session.execute(
                record_chemical_activity.insert().values(
                    record_id=record_id,
                    chemical_activity_id=chemical_activity.id,
                ),
            )

    def load_all_records(
        self,
        transformer_1a,
        transformer_3a,
        transformer_3c,
    ):
        """Load records from different transformers into the Record table after merging with 1b."""
        # Merge 1b data with 1a, 3a, and 3c using both trifid and tri_chem_id
        df_1a_management = self.merge_with_1b(transformer_1a.df_management)
        df_3a_management = self.merge_with_1b(transformer_3a.df_management)
        df_3b_management = self.merge_with_1b(transformer_3c.df_management)
        df_1a_releases = self.merge_with_1b(transformer_1a.df_releases)
        df_3a_releases = self.merge_with_1b(transformer_3a.df_releases)

        # Load records with appropriate handler columns for 3a and 3c
        self.load_records(
            df_1a_management,
            record_type="management",
        )
        self.load_records(
            df_1a_releases,
            record_type="release",
        )
        self.load_records(
            df_3a_management,
            record_type="management",
            handler_columns=(
                "off_site_site_naics_code",
                "off_site_site_naics_title",
            ),
        )
        self.load_records(
            df_3a_releases,
            record_type="release",
        )
        self.load_records(
            df_3b_management,
            record_type="management",
            handler_columns=(
                "naics_code",
                "naics_title",
            ),
        )

    def set_1b(
        self,
        df: pd.DataFrame,
    ):
        """Set the 1b DataFrame."""
        self._df_1b = df


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../../conf",
        job_name="smoke-testing-tri",
    ):
        config = hydra.compose(config_name="main")
        from src.data_processing.create_sqlite_db import create_database

        session = create_database()
        loader = TriDataLoader(config, session)
        loader.load_chemical_activity()
        loader.load_plastic_additives()
