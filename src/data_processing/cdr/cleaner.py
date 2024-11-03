# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""CDR Data Cleaning Module.

This module contains the `CdrDataCleaner` class, which is responsible for
processing and cleaning data related to Chemical Data Reporting (CDR) for
industrial, commercial, and consumer use data.

Classes:
    - CdrDataCleaner: A class designed to load, clean, and process CDR data files
      by applying various cleaning rules, merging with industry data, and preparing
      the data for analysis.

Modules Imported:
    - os: Provides functions for interacting with the operating system.
    - pandas as pd: Used for data manipulation and analysis.
    - omegaconf.DictConfig: Provides structured configuration management.
    - numpy as np: Used for numerical operations, including handling NaN values.

Key Features:
    - Load and clean CDR data files for industrial processing and commercial/consumer use.
    - Clean and standardize NAICS codes and titles.
    - Replace specific values with null (NaN) in given columns.
    - Drop records where all specified columns are null.
    - Convert and validate percentage columns and handle optional dropping of NaN values.
    - Merge data with NAICS industry data for further enrichment.

Functions:
    - `__init__`: Initializes the CdrDataCleaner instance with configuration settings.
    - `_load_cdr_file`: Loads a CDR data file and raises an error if the file is not found.
    - `_clean_naics_code`: Cleans and separates the numeric NAICS code from its title.
    - `_clean_percentage`: Converts the percentage column to numeric and optionally drops NaN rows.
    - `_replace_values_with_null`: Replaces specified values in the DataFrame with null.
    - `_load_naics_industry`: Loads NAICS industry data from a CSV file and renames columns for consistency.
    - `_drop_record_if_all_columns_are_null`: Drops rows from the DataFrame if all specified columns are null.
    - `_clean_data`: Generalized method for loading, cleaning, and processing CDR data.
    - `cleaning_industrial_processing`: Cleans CDR industrial processing data and merges it with NAICS data.
    - `cleaning_commercial_and_consumer_use`: Cleans CDR commercial and consumer use data.

Example Usage:
    Run the module as a script to test the cleaning process:

    ```python
    if __name__ == "__main__":
        import hydra

        with hydra.initialize(
            version_base=None,
            config_path="../../../conf",
            job_name="smoke-testing-tri",
        ):
            cfg = hydra.compose(config_name="main")
            transformer = CdrDataCleaner(cfg, is_drop_nan_percentage=False)
            df_iu = transformer.cleaning_industrial_processing()
            print(df_iu.info())
            print(df_iu.naics_code.head())

            df_ccu = transformer.cleaning_commercial_and_consumer_use()
            print(df_ccu.info())
    ```
"""


import os
from typing import List, Union

import numpy as np
import pandas as pd
from omegaconf import DictConfig

CURRENT_DIRECTORY = os.getcwd()


class CdrDataCleaner:

    def __init__(
        self,
        config: DictConfig,
        is_drop_nan_percentage: bool = True,
    ):
        self.config = config
        self.cdr_config = config.cdr_data
        self.is_drop_nan_percentage = is_drop_nan_percentage
        self.valid_casrn = [chem.CASRN for chem in self.config.plastic_additives.tri_chem_id]

    def _load_cdr_file(
        self,
        file_name: str,
    ) -> pd.DataFrame:
        """Load the CDR data file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        file_path = os.path.join(
            CURRENT_DIRECTORY,
            "data",
            "raw",
            file_name,
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist." " Please check the file path.")

        return pd.read_csv(  # type: ignore [reportCallIssue]
            file_path,
            sep=",",
            quotechar='"',
        )

    def _clean_naics_code(self, naics_code: str) -> Union[tuple[str, str], tuple[None, None]]:
        """
        Clean the NAICS code by separating the numeric code from the title.

        Args:
            naics_code (str): The NAICS code to clean.

        Returns:
            tuple[str, str]: A tuple containing the numeric code and the title.
        """
        if pd.notnull(naics_code) and naics_code != "CBI":
            match = pd.Series(naics_code).str.extract(r"^(\d+)\s*(.*)$")
            numeric_code = match[0][0] if match[0][0] else ""
            title = match[1][0] if match[1][0] else ""
            return numeric_code, title
        else:
            return None, None

    def _clean_percentage(
        self,
        df: pd.DataFrame,
        column: str,
    ) -> pd.DataFrame:
        """Clean the percentage column by converting to numeric values and optionally dropping rows with NaN."""
        df[column] = pd.to_numeric(df[column], errors="coerce")  # type: ignore [reportArgumentType]
        return df.dropna(subset=[column]) if self.is_drop_nan_percentage else df

    def _replace_values_with_null(
        self,
        df: pd.DataFrame,
        columns: List[str],
        values_to_replace: List[str],
    ):
        """Replace specified values with null (NaN) in given columns."""
        for column in columns:
            df[column] = df[column].replace(values_to_replace, np.nan)  # type: ignore [reportArgumentType]

    def _load_naics_industry(self) -> pd.DataFrame:
        """Load the NAICS industry data from the CSV file."""
        df = pd.read_csv(
            os.path.join(
                CURRENT_DIRECTORY,
                "ancillary",
                "cd_is_to_naics.csv",
            ),
            sep=",",
            quotechar='"',
            usecols=[
                "industry_sector_code",
                "naics_code_2017",
                "naics_title",
                "industry_sector_name",
            ],  # type: ignore [reportArgumentType]
            dtype={
                "industry_sector_code": str,
                "naics_code_2017": str,
                "naics_title": str,
                "industry_sector_name": str,
            },
        )
        df.rename(
            columns={
                "naics_code_2017": "industrial_use_naics_code",
                "naics_title": "industrial_use_naics_title",
            },
            inplace=True,
        )
        return df

    def _drop_record_if_all_columns_are_null(
        self,
        df: pd.DataFrame,
        columns: List[str],
    ) -> pd.DataFrame:
        """Drop rows from the DataFrame if all specified columns are null."""
        return df.dropna(subset=columns, how="all")

    def _clean_data(
        self,
        use_config: DictConfig,
        columns_to_clean: List[str],
        columns_of_interest: List[str],
    ) -> pd.DataFrame:
        """
        General method for cleaning CDR data.

        Args:
            use_config (DictConfig): Configuration for the specific type of CDR use.
            columns_to_clean (List[str]): List of columns to clean by replacing specific values with NaN.
            columns_of_interest (List[str]): List of columns to check when dropping rows.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        usecols = list(use_config.needed_columns.values())
        df = self._load_cdr_file(use_config.file)
        df = df[usecols]

        self._replace_values_with_null(df, columns_to_clean, ["Not Known or Reasonably Ascertainable", "CBI", "NKRA"])
        df = df[df[use_config.needed_columns.casrn].astype(str).isin(self.valid_casrn)]  # type: ignore [reportAttributeAccessIssue]
        df = self._clean_percentage(df, use_config.needed_columns.percentage)

        if df.empty:
            raise ValueError(f"CDR {use_config.name} dataframe is empty")

        df.rename(columns={value: key for key, value in use_config.needed_columns.items()}, inplace=True)
        df = df.astype({"casrn": "str", "naics_code": "str"})
        df = self._drop_record_if_all_columns_are_null(df, columns_of_interest)

        return df

    def cleaning_industrial_processing(self) -> pd.DataFrame:
        """Clean the CDR industrial use data and merge with NAICS data."""
        industrial_activities = self.cdr_config.industrial_use
        columns_to_clean = [
            industrial_activities.needed_columns.industrial_type_of_process_or_use,
            industrial_activities.needed_columns.industry_sector_code,
            industrial_activities.needed_columns.industry_function_category,
        ]
        columns_of_interest = [
            "industry_sector_code",
            "industrial_type_of_process_or_use",
            "industry_function_category",
        ]

        df = self._clean_data(industrial_activities, columns_to_clean, columns_of_interest)

        # Merge with NAICS data for industrial processing only
        df_naics = self._load_naics_industry()
        df = pd.merge(df, df_naics, on="industry_sector_code", how="left")

        df[["naics_code", "naics_title"]] = df["naics_code"].apply(self._clean_naics_code).apply(pd.Series)

        return df

    def cleaning_commercial_and_consumer_use(self) -> pd.DataFrame:
        """Clean the CDR commercial and consumer use data."""
        commercial_and_consumer_use = self.cdr_config.commercial_and_consumer_use
        columns_to_clean = [
            commercial_and_consumer_use.needed_columns.consumer_commercial_product_category,
            commercial_and_consumer_use.needed_columns.consumer_commercial_function_category,
            commercial_and_consumer_use.needed_columns.type_of_use,
        ]
        columns_of_interest = [
            "consumer_commercial_product_category",
            "consumer_commercial_function_category",
        ]

        return self._clean_data(commercial_and_consumer_use, columns_to_clean, columns_of_interest)


if __name__ == "__main__":

    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../../conf",
        job_name="smoke-testing-tri",
    ):
        cfg = hydra.compose(config_name="main")
        transformer = CdrDataCleaner(
            cfg,
            is_drop_nan_percentage=False,
        )
        df_iu = transformer.cleaning_industrial_processing()
        print(df_iu.info())

        print(df_iu.naics_code.head())

        df_ccu = transformer.cleaning_commercial_and_consumer_use()
        print(df_ccu.info())
