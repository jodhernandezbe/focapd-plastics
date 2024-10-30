# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for processing and transforming TRI Form R (3C) data files.

This module defines the `TriFile3cTransformer` class, which is responsible for handling
and transforming Toxic Release Inventory (TRI) data specifically for Form R 3C, which
provides details on transfers to Publicly Owned Treatment Works (POTWs). The class
inherits from a base class, `TriFileNumericalTransformer`, designed to modularize
data processing steps to enhance code reuse, readability, and maintainability across
different TRI data file types.

The `TriFile3cTransformer` class integrates several processing steps to achieve a
standardized output format for 3C TRI files:
  - Column Selection: Selects only relevant columns specified in the configuration.
  - Missing Value Handling: Fills missing values, particularly for release and management types.
  - Data Transformation: Prepares the data for analysis by unpivoting wide data to long format, converting values to a consistent unit (kilograms), and performing aggregations.
  - Data Formatting: Formats management columns to improve readability, including renaming and formatting.

TRI Program Background:
The Toxic Release Inventory (TRI) program tracks the management of specific toxic chemicals
that may pose a risk to human health and the environment. Form R 3C specifically focuses on
the transfer of these chemicals to POTWs, which are responsible for treating wastewater
before it is released back into the environment.

Classes:
    TriFile3cTransformer: A specialized transformer for handling and processing TRI Form R (3C) data files.

Example Usage:
    Load the transformer with a configuration file, process the TRI 3C data, and obtain a
    standardized DataFrame output ready for analysis.

    transformer = TriFile3cTransformer(file_name="TRI_3C_data.csv", config=cfg)
    processed_data = transformer.process()
    print(processed_data)

"""

from omegaconf import DictConfig

from src.data_processing.tri.transform.base import TriFileNumericalTransformer


class TriFile3cTransformer(TriFileNumericalTransformer):
    """Class for transforming TRI Form R (3C) data files.

    Attributes:
        file_name (str): The name of the TRI data file.
        file_type (str): The type of TRI data file.
        config (DictConfig): The configuration object.
        data (pd.DataFrame): The data from the TRI data file.

    """

    def __init__(
        self,
        file_name: str,
        config: DictConfig,
    ):
        super().__init__(file_name, "file_3c", False, config)

    def _assign_naics_to_potw(self):
        self.df_management["off_site_site_naics_code"] = self.config.potw_naics_code

    def process(self):
        """Process the TRI data file."""
        needed_columns = self._get_needed_columns()
        self.data = self.select_columns(needed_columns)
        self.data = self.filter_desired_chemicals()
        self.fill_missing_values()
        self.data = self.prepare_unpivot_columns()
        self.to_kilogram()
        self.df_management = self.aggregate_values(self.data)
        self.df_management = self.format_management_column_names(self.df_management)
        self._assign_naics_to_potw()


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../../conf",
        job_name="smoke-testing-tri",
    ):
        cfg = hydra.compose(config_name="main")
        transformer = TriFile3cTransformer("US_3c_2022.txt", cfg)
        transformer.process()
