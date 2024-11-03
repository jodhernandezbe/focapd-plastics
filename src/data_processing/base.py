# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Base module for data loaders.

This module provides the `BaseDataLoader` class, which acts as a foundational
utility for managing database operations such as checking for the existence
of elements, retrieving or creating records, and handling caching mechanisms
to optimize repeated database lookups.

Classes:
    BaseDataLoader: A base class that provides utility methods for loading
        and managing data in a SQLAlchemy-based database.

Attributes:
    config (DictConfig): The configuration object containing settings and options.
    session (Session): The SQLAlchemy session used for database interaction.

Methods:
    __init__(self, config: DictConfig, session: Session):
        Initializes the `BaseDataLoader` with the given configuration and session.

    element_exists(self, model, **kwargs) -> bool:
        Checks if an element exists in the database by querying with specified criteria.

    get_or_create(self, model, **kwargs):
        Retrieves an existing element from the database or creates a new one if it doesn't exist.

    create_element(self, model, **kwargs):
        Creates a new element in the database and returns it.

    _cache_get_or_create(self, cache: Dict[Tuple, int], get_or_create_func: Callable, **kwargs):
        Checks a cache for an existing ID or calls a function to create a new record if not found.
        Updates the cache with the ID or the created element.

    _get_additive_id(self, tri_chem_id: str) -> Union[int, None]:
        Fetches the ID of an `Additive` entry based on its `tri_chemical_id`.
        Returns `None` if no matching record is found.

    _get_industry_sector_id(self, naics_code: Union[str, None], naics_title: Union[str, None]) -> Union[int, None]:
        Fetches or creates an `IndustrySector` entry based on `naics_code` and `naics_title`,
        returning its ID. Returns `None` if the required parameters are missing or invalid.

Usage:
    The `BaseDataLoader` class is intended to be inherited by specific data loader
    classes that need to manage database operations involving various models. It
    provides common methods that simplify the interaction with the database and
    support efficient record management.

Example:
    >>> from sqlalchemy.orm import sessionmaker
    >>> from omegaconf import OmegaConf
    >>> config = OmegaConf.create({"database": {"host": "localhost", "port": 5432}})
    >>> session = sessionmaker(bind=engine)()
    >>> base_loader = BaseDataLoader(config, session)
    >>> additive_id = base_loader._get_additive_id("123-45-6")
    >>> print(f"Additive ID: {additive_id}")
"""


from typing import Callable, Dict, Tuple, Union

from omegaconf import DictConfig
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.data_processing.data_models import Additive, IndustrySector


class BaseDataLoader:
    """Base class for data loaders."""

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
        element = self.session.query(model).filter_by(**kwargs).first()
        if not element:
            element = self.create_element(model, **kwargs)
        return element

    def create_element(self, model, **kwargs):
        """Create an element in the database."""
        element = model(**kwargs)
        self.session.add(element)
        self.session.commit()
        self.session.refresh(element)
        return element

    def _cache_get_or_create(
        self,
        cache: Dict[Tuple, int],
        get_or_create_func: Callable,
        **kwards,
    ):
        """Check cache for existing ID or create a new record if not found."""
        key = tuple(kwards.items())
        if key not in cache:
            element = get_or_create_func(**kwards)
            cache[key] = element if isinstance(element, int) else (element.id if element else None)  # type: ignore [reportArgumentType]
        return cache[key]

    def _get_additive_id(
        self,
        tri_chem_id: str,
    ):
        """Fetch an Additive and return its id."""
        additive = self.session.query(Additive).filter_by(tri_chemical_id=tri_chem_id).first()
        if additive:
            return additive.id
        return None

    def _get_industry_sector_id(
        self,
        naics_code: Union[str, None],
        naics_title: Union[str, None],
    ):
        """Fetch or create IndustrySector and return its id."""
        if naics_code and naics_title:
            sector = self.get_or_create(
                IndustrySector,
                naics_code=naics_code,
                naics_title=naics_title,
            )
            if sector:
                return sector.id
        return None
