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
from typing import List

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
        if unit == "Pounds":
            return cls.POUNDS_TO_KILOGRAMS
        elif unit == "Grams":
            return cls.GRAMS_TO_KILOGRAMS
        else:
            raise ValueError(f"Unknown unit: {unit}")


class TriDataHelper:
    """Helper class for working with TRI data files."""

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
    def load_txt_data(
        cls,
        file_path: str,
        column_names: List[str],
    ) -> pd.DataFrame:
        """Load the data from a text file.

        Args:
          file_path: str: The path to the text file.
          column_names: List[str]: The names of the columns in the data.

        Returns:
          pd.DataFrame: The data from the text file.

        """
        df = pd.read_csv(
            file_path,
            sep="\t",
            header=None,
            encoding="ISO-8859-1",
            low_memory=False,
            skiprows=[0],
            lineterminator="\n",
        )
        df.columns = column_names
        return df
