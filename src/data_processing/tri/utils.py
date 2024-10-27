# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Data processing utils.

Module for utility functions used in data processing tasks, such as loading
data from text files and generating file paths.

This module contains a class with static
methods for generating file paths and loading data from text files.

Classes:
    ConversionFactor: Enum for conversion factors between different units of mass.
    TriDataHelper: Helper class for working with TRI data files.

"""

import os
from enum import Enum
from typing import List, Optional

import pandas as pd

CURRENT_DIRECTORY = os.getcwd()


class ConversionFactor(Enum):
    """Enum for conversion factors between different units of mass.

    Note:
      - Assuming TRI wouldn't change the two ways to report the mass.
      - Pint or other units handler could include if needed in the future,
        if this would be extended beyond the paper scope to ensure scalability
        and mantainability.

    """

    POUNDS_TO_KILOGRAMS = 0.453592
    GRAMS_TO_KILOGRAMS = 10**-3

    @classmethod
    def from_string(cls, unit: str) -> "ConversionFactor":
        """Get the conversion factor from a string representation of the unit.

        Args:
            unit: str: The string representation of the unit.

        Returns:
            ConversionFactor: The corresponding conversion factor enum member.

        Raises:
            ValueError: If the unit is not recognized.

        """
        unit = unit.lower()
        if unit.lower() == "pounds":
            return cls.POUNDS_TO_KILOGRAMS
        elif unit.lower() == "grams":
            return cls.GRAMS_TO_KILOGRAMS
        else:
            raise ValueError(f"Unknown unit: {unit}")


class TriDataHelper:
    """Helper class for working with TRI data files."""

    @classmethod
    def read_file_columns(cls, columns_file_name: str) -> list:
        """Read column names from a text file and return them as a list.

        Args:
            columns_file_name (str): The name of the file containing column names.

        Returns:
            list: A list of column names.

        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: If an error occurs while reading the file.

        """
        try:
            with open(columns_file_name, "r") as file:
                columns = [line.strip() for line in file.readlines()]
            return columns
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {columns_file_name} does not exist.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the file {columns_file_name}: {e}")

    @classmethod
    def generate_data_file_path(
        cls,
        file_name: str,
        subfolder: str = "raw",
    ) -> str:
        """Generate the file path for the data file.

        Args:
          file_name: str: The name of the data file.
          subfolder: str: The subfolder in which the data file is located.

        Returns:
          str: The full path to the data file.

        """
        return os.path.join(
            CURRENT_DIRECTORY,
            "data",
            subfolder,
            file_name,
        )

    @classmethod
    def load_txt_data(cls, file_path: str, column_names: List[str], used_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """Load the data from a text file.

        Args:
          file_path: str: The path to the text file.
          column_names: List[str]: The names of the columns in the data.
          used_cols: Optional[List[str]]: The columns to use from the data.
            If None, all columns are used.

        Returns:
          pd.DataFrame: The data from the text file.

        """
        try:
            df = pd.read_csv(
                file_path,
                sep="\t",
                header=None,
                encoding="ISO-8859-1",
                low_memory=False,
                skiprows=[0],
                lineterminator="\n",
                quotechar='"',
                names=column_names,
                on_bad_lines="skip",
                usecols=used_cols if used_cols else column_names,
            )
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

    @classmethod
    def unpivot_dataframe(
        cls, df: pd.DataFrame, id_vars: List[str], value_vars: List[str], var_name: str = "variable", value_name: str = "value"
    ) -> pd.DataFrame:
        """Unpivot (melt) a DataFrame from wide to long format.

        Args:
            df (pd.DataFrame): The input DataFrame.
            id_vars (List[str]): Columns to use as identifier variables.
            value_vars (List[str]): Columns to unpivot.
            var_name (str): Name of the new column for the variable names (default: 'variable').
            value_name (str): Name of the new column for the variable values (default: 'value').

        Returns:
            pd.DataFrame: The unpivoted DataFrame in long format.
        """
        return pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name)
