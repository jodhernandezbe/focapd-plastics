# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for orchestrating the transformation and loading of CDR data files.

This module defines the `CdrDataOrchestator` class, which is responsible for coordinating
the cleaning, processing, and loading of CDR (Chemical Data Reporting) data files into a
database. It leverages the `CdrDataCleaner` class for data preparation and the `CdrDataLoader`
class for database insertion.

Classes:
    CdrDataOrchestator: Orchestrates the end-to-end process of transforming CDR data files and
        loading them into a database.

Attributes:
    config (DictConfig): The configuration object for managing application settings.
    session (Session): The database session used for interactions with the database.
    cdr_db_loader (CdrDataLoader): An instance of `CdrDataLoader` for loading data into the database.
    cdr_data_cleaner (CdrDataCleaner): An instance of `CdrDataCleaner` for cleaning the input data.

Methods:
    __init__(self, config: DictConfig, is_drop_nan_percentage: bool = False):
        Initializes the `CdrDataOrchestator` with the given configuration and sets up
        the database session and data cleaner and loader instances.

    run(self):
        Processes the CDR data files by cleaning them and loading the cleaned data
        into the database. Closes the database session after processing.

Usage:
    The `CdrDataOrchestator` class can be used to streamline the process of loading CDR data
    from raw files into a database. It ensures that data is cleaned and loaded in a consistent
    and automated manner.

Example:
    >>> from omegaconf import OmegaConf
    >>> config = OmegaConf.load("config.yaml")
    >>> orchestrator = CdrDataOrchestator(config, is_drop_nan_percentage=True)
    >>> orchestrator.run()

"""


from omegaconf import DictConfig

from src.data_processing.cdr.cleaner import CdrDataCleaner
from src.data_processing.cdr.load import CdrDataLoader
from src.data_processing.create_sqlite_db import create_database


class CdrDataOrchestator:
    """Class for orchestrating the transformation of CDR data files."""

    def __init__(
        self,
        config: DictConfig,
        is_drop_nan_percentage: bool = False,
    ):
        self.config = config
        self.session = create_database()
        self.cdr_db_loader = CdrDataLoader(
            config=self.config,
            session=self.session,
        )
        self.cdr_data_cleaner = CdrDataCleaner(
            config=self.config,
            is_drop_nan_percentage=is_drop_nan_percentage,
        )

    def run(self):
        """Process the CDR data files."""
        df_industrial = self.cdr_data_cleaner.cleaning_industrial_processing()
        df_consumer = self.cdr_data_cleaner.cleaning_commercial_and_consumer_use()
        self.cdr_db_loader.load_industrial_use(df_industrial)
        self.cdr_db_loader.load_commercial_and_consumer_use(df_consumer)
        self.session.close()
