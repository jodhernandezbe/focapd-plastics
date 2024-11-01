# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for transforming TRI Form R (3A) data files.

This module defines the `TriFile3aTransformer` class, which inherits from the `TriFileNumericalTransformer`
base class. The transformer is specifically designed to process and transform TRI Form R (3A) data files,
which detail off-site transfers of materials to various facilities. This class leverages both the FRS
(Facility Registry Service) and Census APIs to enrich the data with NAICS (North American Industry
Classification System) codes and descriptions for facilities.

Classes:
    TriFile3aTransformer: Handles the extraction, transformation, and enrichment of TRI Form R (3A) data.

Attributes:
    file_name (str): The name of the TRI data file.
    file_type (str): The type of TRI data file.
    config (DictConfig): Configuration object for setting parameters.
    data (pd.DataFrame): The main DataFrame containing raw or processed TRI data.

Methods:
    __init__(file_name: str, config: DictConfig): Initializes the transformer with file name, file type,
        and configuration settings.
    look_for_offsite_naics_code(): Searches for offsite NAICS codes using the FRS and Census APIs.
        Filters results to exclude null NAICS codes (e.g., for facilities located outside the U.S.),
        merges enriched data into the management DataFrame, and updates the main data.
    process(): Orchestrates the transformation pipeline by selecting required columns, handling missing
        values, converting units, separating release and management records, formatting management
        data, and calling the `look_for_offsite_naics_code` method for data enrichment.

Example Usage:
    ```
    import hydra
    from omegaconf import DictConfig

    # Load configuration using Hydra
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="main")

    # Instantiate and process data
    transformer = TriFile3aTransformer("US_3a_2022.txt", cfg)
    transformer.process()
    ```

Notes:
    - The `look_for_offsite_naics_code` method relies on asynchronous API calls to the FRS and Census APIs
      to fetch and merge relevant NAICS codes, helping provide comprehensive information on off-site facilities.
    - The `process` method utilizes modularized methods from the `TriFileNumericalTransformer` to ensure
      clean and well-structured data transformation.

"""


from omegaconf import DictConfig

from src.data_processing.frs_api_queries import FrsDataFetcher
from src.data_processing.naics_api_queries import NaicsDataFetcher
from src.data_processing.tri.transform.base import TriFileNumericalTransformer


class TriFile3aTransformer(TriFileNumericalTransformer):
    """Class for transforming TRI Form R (3A) data files.

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
        super().__init__(file_name, "file_3a", False, config)
        self.frs_fether = FrsDataFetcher(config)
        self.census_fetcher = NaicsDataFetcher(config)

    def look_for_offsite_naics_code(self):
        """Look for offsite NAICS code in the data."""
        off_site_frs_id_column = self.config.tri_files.file_3a.off_site_frs_id_column
        self.df_management[off_site_frs_id_column] = self.df_management[off_site_frs_id_column].astype(int).astype(str)

        # Some times it could return a null naics code because the offsite is located outside the U.S.
        frs_results = self.frs_fether.process_registry_ids(
            self.df_management,
            off_site_frs_id_column,
        )
        frs_results.dropna(
            subset=["naics_code"],
            inplace=True,
        )
        naics_results = self.census_fetcher.process_naics_codes(frs_results, "naics_code")

        merged_df = self.df_management.merge(
            frs_results,
            left_on=off_site_frs_id_column,
            right_on="registry_id",
            how="left",
        )

        merged_df = merged_df.merge(
            naics_results,
            on="naics_code",
            how="left",
        )
        merged_df = merged_df.drop(columns=["registry_id"])
        self.df_management = merged_df

    def process(self):
        """Process the TRI data file."""
        needed_columns = self._get_needed_columns()
        self.data = self.select_columns(needed_columns)
        self.data = self.filter_desired_chemicals()
        self.fill_missing_values()
        self.data = self.prepare_unpivot_columns()
        self.to_kilogram()
        self.df_releases, self.df_management = self.separate_releases_and_management()
        self.df_releases = self.organize_resealse_dataframe(self.df_releases)
        self.df_management = self.organize_management_dataframe(self.df_management)
        self.look_for_offsite_naics_code()


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../../conf",
        job_name="smoke-testing-tri",
    ):
        cfg = hydra.compose(config_name="main")
        transformer = TriFile3aTransformer("US_3a_2022.txt", cfg)
        transformer.process()
        print(transformer.df_management.info())
        print(transformer.df_releases.info())
