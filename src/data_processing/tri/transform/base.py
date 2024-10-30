# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Base module for transforming TRI data files.

This module defines classes and methods for general and numerical transformations of
TRI (Toxics Release Inventory) data files. The classes here provide common functionalities
to streamline the data transformation process, allowing for specialized processing and
aggregation of TRI data, including the handling of various column types, unit conversions,
and separating release and management data for further analysis.

Classes:
    TriFileBaseTransformer: Base class for transforming TRI data files, providing essential methods
                            for data loading, column selection, and general transformation operations.
    TriFileNumericalTransformer: Extension of TriFileBaseTransformer, which includes numerical
                                 transformations, unit conversions, and additional methods for
                                 separating release and management data.

Attributes:
    CURRENT_DIRECTORY (str): Stores the current working directory path.

Methods:
    __init__(file_name: str, file_type: str, config: DictConfig): Initializes the transformer with
        the specified file name, file type, and configuration settings.
    load_data(file_name: str) -> pd.DataFrame: Loads TRI data from a text file.
    prepare_unpivot_columns() -> pd.DataFrame: Unpivots the data for standardized long format.
    fill_missing_values(): Fills NaN values in specific columns with zeros.
    separate_releases_and_management() -> Tuple[pd.DataFrame, pd.DataFrame]: Separates data into release
        and management subsets based on configuration.
    organize_management_dataframe(df_management: pd.DataFrame) -> pd.DataFrame: Organizes and formats
        management data column names for analysis.

Usage Example:
    ```
    from omegaconf import DictConfig

    # Load configuration with Hydra or another method
    config = DictConfig({...})

    # Initialize and process TRI data for File Type 1A
    transformer = TriFileNumericalTransformer("US_1a_2022.txt", "file_1a", config)
    transformer.process()
    ```

Notes:
    - This module depends on a well-defined configuration file (DictConfig) for specifying TRI file structures
      and relevant data columns.
    - Custom transformation methods such as `to_kilogram()` handle specific data conversions required
      by the TRI format.
    - Error handling ensures robust data processing, with warnings and exceptions when configuration
      elements or data columns are missing.

"""

import os
from typing import Dict, List, Tuple, cast

import pandas as pd
from omegaconf import DictConfig

from src.data_processing.tri.utils import ConversionFactor, TriDataHelper

CURRENT_DIRECTORY = os.getcwd()


class TriFileBaseTransformer:
    """Base class for transforming TRI data files.

    Attributes:
        file_name (str): The name of the TRI data file.
        file_type (str): The type of TRI data file.
        config (DictConfig): The configuration object.
        data (pd.DataFrame): The data from the TRI data file.

    """

    def __init__(
        self,
        file_name: str,
        file_type: str,
        config: DictConfig,
    ):
        self.config = config
        self.file_type = file_type
        self._column_names: List[str]
        self._var_and_value_names: Dict[str, str]
        self.data = self.load_data(file_name)

    @property
    def column_names(self) -> List[str]:
        """Get the column names needed for the file type.

        Returns:
            List[str]: A list of column names needed for the file type.

        Raises:
            KeyError: If the column names are not found.

        """
        if not hasattr(self, "_column_names"):
            columns_file_name = self._get_path_to_columns()
            self._column_names = TriDataHelper.read_file_columns(columns_file_name)
        return self._column_names

    @property
    def var_and_value_names(self) -> Dict[str, str]:
        """Get the 'var_name' and 'value_name' attributes from the configuration file.

        Returns:
            Dict[str, str]: A dictionary containing the 'var_name' and 'value_name' attributes.

        Raises:
            EnvironmentError: If the 'var_name' or 'value_name' attributes are not found.

        """
        if not hasattr(self, "_var_and_value_names"):
            self._var_and_value_names = self._get_var_and_value_names()
        return self._var_and_value_names

    def filter_desired_chemicals(self):
        """Filter the data to include only the desired chemicals.

        Returns:
            pd.DataFrame: The filtered data.

        """
        plastic_additives = [chem["CASRN"] for chem in self.config.plastic_additives.tri_chem_id]
        self._organize_tri_chem_id()
        return self.data.loc[self.data.tri_chem_id.isin(plastic_additives)]

    def _organize_tri_chem_id(self):
        self.data.tri_chem_id = self.data.tri_chem_id.str.replace("-", "").str.lstrip("0")

    def _get_path_to_columns(self) -> str:
        """Get the path to the columns file.

        Returns:
            str: The path to the columns file.

        """
        return os.path.join(
            CURRENT_DIRECTORY,
            self.config.tri_files.columns_folder,
            self.config.tri_files[self.file_type].columns_file,
        )

    def _get_needed_columns(self) -> List[str]:
        """Get the column names needed for the file type.

        Returns:
            List[str]: A list of column names needed for the file type.

        Raises:
            KeyError: If the column names are not found.

        """
        try:
            return [col["name"] for col in self.config.tri_files[self.file_type].needed_columns]
        except KeyError:
            raise KeyError(f"Column names not found for file type: {self.file_type}")

    def select_columns(
        self,
        columns: List[str],
    ) -> pd.DataFrame:
        """Select only the specified columns from the DataFrame.

        Args:
            columns (List[str]): A list of column names to keep in the DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing only the specified columns.
        """
        # Ensure the desired columns exist in the DataFrame to avoid KeyError
        existing_columns = [col for col in columns if col in self.data]
        if len(existing_columns) < len(columns):
            missing = set(columns) - set(existing_columns)
            print(f"Warning: These columns were not found in the DataFrame and will be ignored: {missing}")

        return self.data[existing_columns]  # type: ignore [reportReturnType]

    def fill_missing_values(self):
        """Fill null values in columns with 'relase_type' or 'management_type' to 0.0."""
        columns_to_fill = self._get_columns_with_attributes()
        self.data[columns_to_fill] = self.data[columns_to_fill].fillna(0.0)

    def _get_columns_with_attributes(self) -> List[str]:
        """Extracts columns with 'relase_type' or 'management_type' attributes from config.

        Returns:
            List[str]: A list of column names with 'relase_type' or 'management_type' attributes.

        """
        return [
            column.name
            for column in self.config.tri_files[self.file_type].needed_columns
            if "relase_type" in column or "management_type" in column
        ]

    def _get_id_vars(self) -> List[str]:
        """Get identifier columns (id_vars) based on 'is_general_info' in config."""
        return [
            column.name
            for column in self.config.tri_files[self.file_type].needed_columns
            if getattr(column, "is_general_info", False)
        ]

    def _get_value_vars(self) -> List[str]:
        """Get value columns (value_vars) as those not marked with 'is_general_info'."""
        return [
            column.name
            for column in self.config.tri_files[self.file_type].needed_columns
            if not getattr(column, "is_general_info", False)
        ]

    def _get_var_and_value_names(self) -> Dict[str, str]:
        """Retrieve 'var_name' and 'value_name' from config with error handling."""
        var_name = self.config.tri_files[self.file_type].get("var_name")
        value_name = self.config.tri_files[self.file_type].get("value_name")

        if not var_name or not value_name:
            missing_field = "var_name" if not var_name else "value_name"
            raise EnvironmentError(
                f"The '{missing_field}' attribute is required in the configuration file for {self.file_type}."
            )

        return {"var_name": var_name, "value_name": value_name}

    def prepare_unpivot_columns(self) -> pd.DataFrame:
        """Prepare and unpivot the DataFrame based on the configuration for id_vars and value_vars.

        Returns:
            pd.DataFrame: The unpivoted DataFrame in long format.
        """
        id_vars = self._get_id_vars()
        value_vars = self._get_value_vars()

        return TriDataHelper.unpivot_dataframe(
            self.data,
            id_vars=id_vars,
            value_vars=value_vars,
            var_name=self.var_and_value_names["var_name"],
            value_name=self.var_and_value_names["value_name"],
        )

    def load_data(self, file_name: str) -> pd.DataFrame:
        """Load the data from the TRI data file.

        Args:
            file_name (str): The name of the TRI data file.

        Returns:
            pd.DataFrame: The data from the TRI data file.

        Raises:
            FileNotFoundError: If the file is not found.

        """
        file_path = TriDataHelper.generate_data_file_path(
            file_name=file_name,
        )
        try:
            return TriDataHelper.load_txt_data(
                file_path=file_path,
                column_names=self.column_names,
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")


class TriFileNumericalTransformer(TriFileBaseTransformer):
    """Class for transforming TRI data files with numerical values.

    Attributes:
        file_name (str): The name of the TRI data file.
        file_type (str): The type of TRI data file.
        config (DictConfig): The configuration object.
        data (pd.DataFrame): The data from the TRI data file.

    """

    def __init__(
        self,
        file_name: str,
        file_type: str,
        is_on_site: bool,
        config: DictConfig,
    ):
        super().__init__(file_name, file_type, config)
        self._management_data: pd.DataFrame
        self.is_on_site = is_on_site

    def _get_unit_column(self) -> str:
        """Retrieve the column marked as 'is_unit_of_measure' in the config.

        Returns:
            str: The name of the column marked as 'is_unit_of_measure'.

        """
        for column in self.config.tri_files[self.file_type].needed_columns:
            if getattr(column, "is_unit_of_measure", False):
                return column.name

        raise EnvironmentError(
            f"The 'is_unit_of_measure' attribute is required in the configuration file for {self.file_type}."
        )

    def apply_conversion(
        self,
        value: float,
        unit: str,
    ) -> float:
        """Apply a conversion factor to the value based on the unit of measure.

        Note:
            - Feel free to modify to Pint or other physical units handler package.

        Args:
            value (float): The value to convert.
            unit (str): The unit of measure.

        Returns:
            float: The converted value. If the value cannot be converted it returns -1.0

        """
        try:
            conversion_factor = ConversionFactor.from_string(unit)
            return float(value) * conversion_factor.value
        except Exception as e:
            print(f"Conversion error for unit '{unit}': {e}")
            return -1.0

    def to_kilogram(self):
        """Convert the value column to kilograms based on the unit of measure."""
        value_column = self.var_and_value_names["value_name"]
        if value_column not in self.data.columns:
            raise KeyError(
                f"The value column '{value_column}' specified in configuration does not exist in the {self.file_type} data."
            )

        unit_column = self._get_unit_column()

        self.data[value_column] = self.data.apply(
            lambda row: self.apply_conversion(row[value_column], row[unit_column]), axis=1
        )
        self._drop_no_converted_rows(value_column)
        self._drop_measure_unit_column(unit_column)

    def aggregate_values(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Aggregate the values in 'value_column' by summing over other columns.

        This method groups the data by all columns except the 'value_column' and
        sums the 'value_column' values within each group.

        Args:
            df (pd.DataFrame): The DataFrame to aggregate.

        Returns:
            pd.DataFrame: The aggregated DataFrame.

        """
        value_column = self.var_and_value_names["value_name"]

        # Ensure value_column exists in the data
        if value_column not in df.columns:
            raise KeyError(f"The value column '{value_column}' specified in configuration does not exist in the data.")

        group_columns = [col for col in df.columns if col != value_column]
        aggregated_df = df.groupby(group_columns, as_index=False)[value_column].sum()
        return cast(pd.DataFrame, aggregated_df)

    def separate_releases_and_management(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Separate DataFrame into releases and management based on configuration.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Two DataFrames, one for releases and another for management.

        """
        self._get_release_and_management_columns()

        var_name = self.var_and_value_names["var_name"]

        # Filter data based on release and management columns
        df_releases = self.data[self.data[var_name].isin(self.release_columns)]  # type: ignore [reportAttributeAccessIssue]

        df_management = self.data.loc[self.data[var_name].isin(self.management_columns)]  # type: ignore [reportAttributeAccessIssue]

        return df_releases, df_management  # type: ignore [reportReturnType]

    def organize_resealse_dataframe(self, df_releases: pd.DataFrame) -> pd.DataFrame:
        """Organize the releases DataFrame by mapping release types and formatting column names.

        Args:
            df_releases (pd.DataFrame): The DataFrame containing release data.

        Returns:
            pd.DataFrame: The updated DataFrame with formatted column values.

        """
        df_releases = self.map_release_types(
            df_releases,
        )
        df_releases = self.aggregate_values(df_releases)
        return df_releases

    def organize_management_dataframe(self, df_management: pd.DataFrame) -> pd.DataFrame:
        """Organize the management DataFrame by formatting column names.

        Args:
            df_management (pd.DataFrame): The DataFrame containing management data.

        Returns:
            pd.DataFrame: The updated DataFrame with formatted column values.

        """
        df_management = self.aggregate_values(df_management)
        df_management = self.format_management_column_names(df_management)
        return df_management

    def map_release_types(
        self,
        df_releases: pd.DataFrame,
    ) -> pd.DataFrame:
        """Map release types based on configuration.

        Args:
            df_releases (pd.DataFrame): The DataFrame containing release data.

        """
        df_releases.loc[:, self.var_and_value_names["var_name"]] = df_releases[self.var_and_value_names["var_name"]].map(
            self.release_type_mapping  # type: ignore [reportArgumentType]
        )
        return df_releases

    def format_management_column_names(self, df_management: pd.DataFrame) -> pd.DataFrame:
        """Format the column names of the management DataFrame.

        Format the values in the specified management column by replacing underscores
        with spaces and capitalizing only the first letter of the entire string.

        Args:
            df_management (pd.DataFrame): The DataFrame containing management data.

        Returns:
            pd.DataFrame: Updated DataFrame with formatted column values.

        """
        # Create a mapping for the management column values to the desired format
        column_value_mapping = {
            col: col.replace("_", " ").capitalize() for col in df_management[self.var_and_value_names["var_name"]].unique()
        }

        df_management.loc[:, self.var_and_value_names["var_name"]] = df_management.loc[
            :, self.var_and_value_names["var_name"]
        ].map(column_value_mapping)

        return df_management

    def _drop_no_converted_rows(
        self,
        value_column: str,
    ):
        self.data = self.data[self.data[value_column] != -1.0]

    def _drop_measure_unit_column(
        self,
        unit_column: str,
    ):
        self.data = self.data.drop(columns=[unit_column])

    def _get_release_and_management_columns(self):
        self.release_columns = []
        self.management_columns = []
        self.release_type_mapping = {}

        for column in self.config.tri_files[self.file_type].needed_columns:
            column_name = column.name
            if getattr(column, "relase_type", None):
                self.release_columns.append(column_name)
                self.release_type_mapping[column_name] = column.relase_type
            elif getattr(column, "management_type", None):
                self.management_columns.append(column_name)

    @property
    def management_data(self) -> pd.DataFrame:
        """Generate a DataFrame containing management-related columns.

        This property selects columns related to waste management based on configuration
        settings, and formats column names by replacing underscores with spaces and
        capitalizing only the first letter.

        Returns:
            pd.DataFrame: DataFrame with selected management columns.
        """
        if not hasattr(self, "_management_data"):
            self._management_data = self._organize_management_dataframe()
        return self._management_data

    def _normalize_column_name(self, column_name: str) -> str:
        """Normalize column names by replacing underscores and capitalizing first letter."""
        return column_name.replace("_", " ").capitalize()

    def _organize_management_dataframe(self):
        """Organize the management DataFrame by formatting column names."""
        management_columns = []

        relevant_keys = [
            "is_hazardous_waste",
            "is_landfilling",
            "is_recycling",
            "is_brokering",
            "is_incineration",
            "is_wastewater",
            "is_metal",
            "is_potw",
        ]

        for column in self.config.tri_files[self.file_type].needed_columns:
            if "management_type" in column:
                formatted_column = {
                    "column_name": self._normalize_column_name(column.name),
                    "management_type": column["management_type"],
                }

                for key in relevant_keys:
                    formatted_column[key] = column.get(key, False)

                management_columns.append(formatted_column)

        df = pd.DataFrame(management_columns)
        df["is_on_site"] = self.is_on_site

        return df
