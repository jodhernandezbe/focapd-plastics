# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Orchestration module for the TRI data processing pipeline."""

import os

from hydra import compose, initialize_config_dir

from src.data_processing.tri.transform.file_1a import TriFile1aTransformer
from src.data_processing.tri.transform.file_1b import TriFile1bTransformer
from src.data_processing.tri.transform.file_3a import TriFile3aTransformer
from src.data_processing.tri.transform.file_3c import TriFile3cTransformer


class TriOrchestator:
    """Class for orchestrating the transformation of TRI data files."""

    def __init__(self, year: int):
        self.year = year
        self._generic_file_name = "US_{file_type}_{year}.txt"
        self._initialize_config()

    def _initialize_config(self):
        config_dir: str = "../../../../conf"
        job_name: str = "tri-processing"
        initialize_config_dir(config_dir=os.path.abspath(config_dir), job_name=job_name)
        self.config = compose(config_name="main")

    def process(self):
        """Process the TRI data files."""
        transformer_1b = TriFile1bTransformer(
            self._generic_file_name.format(
                file_type="1b",
                year=self.year,
            ),
            self.config,
        )
        transformer_1b.process()

        transformer_1a = TriFile1aTransformer(
            self._generic_file_name.format(
                file_type="1a",
                year=self.year,
            ),
            self.config,
        )
        transformer_1a.process()

        transformer_3a = TriFile3aTransformer(
            self._generic_file_name.format(
                file_type="3a",
                year=self.year,
            ),
            self.config,
        )
        transformer_3a.process()

        transformer_3c = TriFile3cTransformer(
            self._generic_file_name.format(
                file_type="3c",
                year=self.year,
            ),
            self.config,
        )
        transformer_3c.process()

    def run(self):
        """Run the TRI data processing pipeline."""
        self.process()
