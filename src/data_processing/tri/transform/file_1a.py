# -*- coding: utf-8 -*-
# !/usr/bin/env python


"""Module for transforming TRI Form R (1A) data files.

This module provides the `TriFile1aTransformer` class, specifically designed to process and transform
TRI Form R (1A) data files. Form R (1A) files contain summary information on facility details, chemical releases,
and other waste management activities. This class performs data extraction, transformation, and normalization
to prepare the data for analysis.

Classes:
    TriFile1aTransformer: Handles the transformation of TRI Form R (1A) data, managing tasks such as column selection,
                          data preparation, unit conversions, and dataset organization.

Attributes:
    file_name (str): The name of the TRI data file.
    file_type (str): The type of TRI data file.
    config (DictConfig): Configuration object for specifying data requirements and parameters.
    data (pd.DataFrame): The primary DataFrame for storing and transforming TRI data.

Methods:
    __init__(file_name: str, config: DictConfig): Initializes the transformer with file name, file type,
        and configuration settings.
    process(): Executes the complete data processing pipeline, including:
        - Column selection based on required fields.
        - Handling missing values.
        - Preparing the data in a long format suitable for analysis.
        - Converting units to kilograms for consistency.
        - Separating release and management data.
        - Organizing release and management data for structured analysis.

Example Usage:
    ```
    import hydra
    from omegaconf import DictConfig

    # Load configuration using Hydra
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="main")

    # Instantiate and process the data
    transformer = TriFile1aTransformer("US_1a_2022.txt", cfg)
    transformer.process()
    ```

Notes:
    - The method `separate_releases_and_management` divides the data into two parts: one containing release information
      and another with waste management details, allowing for more targeted analysis.
    - This class assumes that unit conversions to kilograms are required, making it suitable for standardized analyses.
    - Configuration settings (through `DictConfig`) enable flexible management of the data pipeline and ensure consistency
      with other TRI data transformations.

"""


from omegaconf import DictConfig

from src.data_processing.tri.transform.base import TriFileNumericalTransformer


class TriFile1aTransformer(TriFileNumericalTransformer):
    """Class for transforming TRI Form R (1A) data files.

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
        super().__init__(file_name, "file_1a", True, config)

    def process(self):
        """Process the TRI data file."""
        needed_columns = self._get_needed_columns()
        self.data = self.select_columns(needed_columns)
        self.fill_missing_values()
        self.data = self.prepare_unpivot_columns()
        self.to_kilogram()
        self.df_releases, self.df_management = self.separate_releases_and_management()
        self.df_releases = self.organize_resealse_dataframe(self.df_releases)
        self.df_management = self.organize_management_dataframe(self.df_management)


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../../conf",
        job_name="smoke-testing-tri",
    ):
        cfg = hydra.compose(config_name="main")
        transformer = TriFile1aTransformer("US_1a_2022.txt", cfg)
        transformer.process()
