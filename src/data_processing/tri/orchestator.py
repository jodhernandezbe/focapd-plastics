# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Orchestration module for the TRI data processing pipeline.

This module provides a class, `TriOrchestator`, which orchestrates the data
processing pipeline for handling TRI (Toxic Release Inventory) data. The TRI data
processing involves reading, transforming, and loading various data files into an SQLite
database for further analysis.

Classes:
    - TriOrchestator: A class for coordinating the end-to-end processing of TRI data files,
      including loading, transforming, and storing data in the database.

Modules Imported:
    - DictConfig: Used for handling configuration settings.
    - create_database: A function for setting up and creating an SQLite database session.
    - TriDataLoader: A class responsible for loading TRI data into the database.
    - TriFile1aTransformer, TriFile1bTransformer, TriFile3aTransformer, TriFile3cTransformer:
      Classes for transforming different types of TRI data files.

Functionality:
    - Initializes an SQLite database session and a TRI data loader instance.
    - Processes various TRI data files (1A, 1B, 3A, 3C) using corresponding transformer classes.
    - Loads specific data into the database, including chemical activity and plastic additives.
    - Manages and releases data using helper methods for different TRI data file types.

Methods:
    - `__init__`: Initializes the `TriOrchestator` class with a specified year and configuration.
    - `process_file`: A helper method that processes a specific TRI data file using a transformer class.
    - `process_1b`: Processes the TRI 1B data file.
    - `process_1a`: Processes the TRI 1A data file.
    - `process_3a`: Processes the TRI 3A data file.
    - `process_3c`: Processes the TRI 3C data file.
    - `run`: Coordinates the overall data processing workflow, loading data into the database
      and handling specific data transformations and loading tasks.
"""


from omegaconf import DictConfig

from src.data_processing.create_sqlite_db import create_database
from src.data_processing.tri.load.load import TriDataLoader
from src.data_processing.tri.transform.file_1a import TriFile1aTransformer
from src.data_processing.tri.transform.file_1b import TriFile1bTransformer
from src.data_processing.tri.transform.file_3a import TriFile3aTransformer
from src.data_processing.tri.transform.file_3c import TriFile3cTransformer


class TriOrchestator:
    """Class for orchestrating the transformation of TRI data files."""

    def __init__(
        self,
        year: int,
        config: DictConfig,
    ):
        self.year = year
        self.config = config
        self.session = create_database()
        self.tri_db_loader = TriDataLoader(
            config=self.config,
            session=self.session,
        )
        self._generic_file_name = "US_{file_type}_{year}.txt"

    def process_file(self, file_type, transformer_class):
        """Helper method to process a TRI data file based on file type."""
        transformer = transformer_class(
            self._generic_file_name.format(
                file_type=file_type,
                year=self.year,
            ),
            self.config,
        )
        transformer.process()
        return transformer

    def process_1b(self):
        """Process the TRI 1B data file."""
        return self.process_file("1b", TriFile1bTransformer)

    def process_1a(self):
        """Process the TRI 1A data file."""
        return self.process_file("1a", TriFile1aTransformer)

    def process_3a(self):
        """Process the TRI 3A data file."""
        return self.process_file("3a", TriFile3aTransformer)

    def process_3c(self):
        """Process the TRI 3C data file."""
        return self.process_file("3c", TriFile3cTransformer)

    def run(self):
        """Process the TRI data files."""
        self.tri_db_loader.load_chemical_activity()
        self.tri_db_loader.load_plastic_additives()

        transformers = {
            "1b": self.process_1b(),
            "1a": self.process_1a(),
            "3a": self.process_3a(),
            "3c": self.process_3c(),
        }

        # Load management and release data as applicable
        for file_type, transformer in transformers.items():
            if file_type in ["1a", "3a", "3c"]:
                self.tri_db_loader.load_release_management_type(
                    transformer.management_data,
                    "end_of_life_activity",
                )
            if file_type in ["1a", "3a"]:
                self.tri_db_loader.load_release_management_type(
                    transformer.release_data,
                    "release_type",
                )

        self.tri_db_loader.set_1b(
            transformers["1b"].data,
        )

        self.tri_db_loader.load_all_records(
            transformers["1a"],
            transformers["3a"],
            transformers["3c"],
        )
