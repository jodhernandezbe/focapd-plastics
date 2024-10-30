# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Data processing main module.

Module for data processing tasks, such as loading and cleaning TRI data files.
Provides a streamlined data processing pipeline using the `PlasticAdditiveDataEngineering` class
to handle logging, orchestration, and execution.

"""

import logging

from src.data_processing.create_sqlite_db import create_database
from src.data_processing.tri.orchestator import TriOrchestator


class PlasticAdditiveDataEngineering:
    """Class for orchestrating the data processing pipeline for TRI data.

    This class provides an interface for setting up, running, and logging
    the data processing pipeline. The pipeline is designed to load, process,
    and clean data files containing information on plastic additives, specifically
    from the TRI (Toxics Release Inventory) dataset.

    Attributes:
        year (int): The year of the TRI data being processed.
        tri_orchestator (TriOrchestator): An instance of the TriOrchestator class,
            responsible for orchestrating specific data processing steps for the specified year.

    Methods:
        setup_logging(): Sets up the logging configuration for tracking pipeline execution.
        run(): Executes the data processing pipeline and logs the start and completion.

    """

    def __init__(
        self,
        year: int,
    ):
        self.year = year
        self.tri_orchestator = TriOrchestator(year=year)
        self._create_db_tables()
        self.setup_logging()

    def _create_db_tables(self):
        """Create database tables for storing processed data."""
        self.session = create_database()

    def setup_logging(self):
        """Sets up logging configuration."""
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(message)s",
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the data processing pipeline."""
        self.logger.info(f"Running data processing pipeline for the year {self.year}...")
        self.tri_orchestator.run()
        self.logger.info("Data processing pipeline completed.")
