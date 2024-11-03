# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for transforming TRI Form R (1B) data files.

This module defines the `TriFile1bTransformer` class, specifically designed for processing
and transforming TRI Form R (1B) data files, which detail chemical activities and uses at facilities.
The transformer leverages the NAICS API for enriching the data with NAICS descriptions.

Classes:
    TriFile1bTransformer: Handles the extraction, transformation, and enrichment of TRI Form R (1B) data.

Attributes:
    file_name (str): The name of the TRI data file.
    file_type (str): The type of TRI data file.
    config (DictConfig): Configuration object for setting parameters.
    data (pd.DataFrame): The main DataFrame containing raw or processed TRI data.

Methods:
    __init__(file_name: str, config: DictConfig): Initializes the transformer with file name, file type,
        and configuration settings, and sets up the NAICS data fetcher.
    aggregate_yes_no() -> pd.DataFrame: Aggregates the data by grouping on all columns except a
        specified "Yes/No" column. For each group, if any entry in the "Yes/No" column is 'Yes',
        the aggregated value for the group will be 'Yes'; otherwise, it will be 'No'.
    process(): Orchestrates the full data transformation by selecting required columns, preparing
        the data for aggregation, enriching with NAICS descriptions, and applying Yes/No aggregation.

Example Usage:
    ```
    import hydra
    from omegaconf import DictConfig

    # Load configuration using Hydra
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="main")

    # Instantiate and process data
    transformer = TriFile1bTransformer("US_1b_2022.txt", cfg)
    transformer.process()
    ```

"""

from typing import cast

import pandas as pd
from omegaconf import DictConfig

from src.data_processing.tri.transform.base import TriFileBaseTransformer


class TriFile1bTransformer(TriFileBaseTransformer):
    """Class for transforming TRI Form R (1B) data files.

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
        super().__init__(file_name, "file_1b", config)

    def aggregate_yes_no(self) -> pd.DataFrame:
        """Aggregate the DataFrame based on Yes/No values in a specified column.

        Returns:
            pd.DataFrame: Aggregated DataFrame where each group has a Yes if any entry in the
                          value_column is Yes, otherwise No.
        """
        value_column = self.var_and_value_names["value_name"]

        # Ensure value_column exists in the data
        if value_column not in self.data.columns:
            raise KeyError(f"The value column '{value_column}' specified in configuration does not exist in the file_1b data.")

        group_columns = [col for col in self.data.columns if col != value_column]

        aggregated_df = self.data.groupby(group_columns, as_index=False).agg(
            {value_column: lambda x: "Yes" if "Yes" in x.values else "No"}
        )

        return cast(pd.DataFrame, aggregated_df)

    def process(self):
        """Process the TRI data file."""
        needed_columns = self._get_needed_columns()
        self.data = self.select_columns(needed_columns)
        self.data = self.filter_desired_chemicals()
        self.data = self.prepare_unpivot_columns()
        self.data["is_performed"] = self.data["is_performed"].fillna("No")
        self.data = self.aggregate_yes_no()

        if self.data.empty:
            raise ValueError("The data is empty after processing. Please check the configuration settings and the input data.")


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../../conf",
        job_name="smoke-testing-tri",
    ):
        cfg = hydra.compose(config_name="main")
        transformer = TriFile1bTransformer("US_1b_2022.txt", cfg)
        transformer.process()
        print(transformer.data.info())
