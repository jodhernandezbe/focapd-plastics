# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Load data into database."""

from omegaconf import DictConfig
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker

from src.data_processing.data_models import Additive, ChemicalActivity


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
