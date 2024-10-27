# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for fetching NAICS code descriptions from the U.S. Census Bureau API.

This module defines a `NaicsDataFetcher` class, which handles querying the U.S. Census Bureau's
API to retrieve descriptions for NAICS (North American Industry Classification System) codes.
The class supports asynchronous requests for improved efficiency, particularly when fetching
data for multiple unique NAICS codes, and manages API key loading securely from an `.env` file.

Classes:
    NaicsDataFetcher: Encapsulates methods to load the Census API key, fetch data for a single
                      NAICS code, fetch data for multiple codes, and process a DataFrame of
                      NAICS codes to retrieve corresponding descriptions.

Functions:
    __init__(cfg: DictConfig): Initializes the `NaicsDataFetcher` with a configuration object
                               and loads the API key from the `.env` file.
    _load_api_key() -> str: Loads the Census API key from the `.env` file, raising an
                            `EnvironmentError` if the file or key is missing.
    _fetch_single_naics_data(naics_code: str, session: aiohttp.ClientSession) -> Dict[str, Optional[str]]:
        Asynchronously fetches a description for a single NAICS code using a shared session.
    _fetch_all_naics_data(naics_codes: List[str]) -> List[Dict[str, Optional[str]]]:
        Asynchronously fetches descriptions for multiple NAICS codes using a single session.
    process_naics_codes(df: pd.DataFrame, code_column: str) -> pd.DataFrame:
        Processes a DataFrame containing NAICS codes, fetching descriptions and returning
        a new DataFrame with `naics_code` and `naics_title` columns.

Example Usage:
    ```
    import hydra
    from omegaconf import DictConfig
    from dotenv import load_dotenv
    import pandas as pd

    # Load configuration using Hydra
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="main")

    # Example DataFrame with NAICS codes
    df = pd.DataFrame({"naics_code": ["481112", "523910", "621111"]})

    # Create an instance of the NaicsDataFetcher and fetch data
    try:
        fetcher = NaicsDataFetcher(cfg)
        result_df = fetcher.process_naics_codes(df, "naics_code")
        print(result_df)
    except EnvironmentError as e:
        print(e)
    ```

Notes:
    - Requires `aiohttp` for asynchronous HTTP requests, `omegaconf` for configuration handling,
      and `dotenv` to load environment variables.
    - The API key must be stored in an `.env` file with the key `CENSUS_DATA_API_KEY`.
    - Asynchronous requests are used to enhance performance when querying multiple codes.

"""

import asyncio
import os
from typing import Dict, List, Optional

import aiohttp
import pandas as pd
from dotenv import load_dotenv
from omegaconf import DictConfig


class NaicsDataFetcher:
    """Class for fetching NAICS code descriptions from the Census API."""

    def __init__(
        self,
        cfg: DictConfig,
    ):
        """Initialize the NaicsDataFetcher with configuration and API key.

        Args:
            cfg (DictConfig): The configuration object.

        """
        self.cfg = cfg
        self.census_api_key = self._load_api_key()
        self.base_url = f"{cfg.census_api.base_url}/{cfg.census_api.year}/{cfg.census_api.dataset}"

    def _load_api_key(self) -> str:
        """Load the Census API key from the .env file.

        Returns:
            str: The API key for the Census Bureau.

        Raises:
            EnvironmentError: If the .env file or the CENSUS_DATA_API_KEY is not found.

        """
        load_dotenv()
        api_key = os.getenv("CENSUS_DATA_API_KEY")

        if not api_key:
            raise EnvironmentError(
                "CENSUS_DATA_API_KEY not found. Please ensure the .env file is present and contains the API key."
            )
        return api_key

    async def _fetch_single_naics_data(
        self,
        naics_code: str,
        session: aiohttp.ClientSession,
    ) -> Dict[str, Optional[str]]:
        """Fetch data for a single NAICS code asynchronously using a shared session.

        Args:
            naics_code (str): The NAICS code to fetch data for.
            session (aiohttp.ClientSession): The shared aiohttp session.

        Returns:
            Dict[str, Optional[str]]: A dictionary with `naics_code` and `naics_title`.
        """
        full_url = (
            f"{self.base_url}"
            f"?get={self.cfg.census_api.parameters['get']}"
            f"&for={self.cfg.census_api.parameters['for_']}"
            f"&{self.cfg.census_api.parameters['naics_code'].format(naics_code=naics_code)}"
            f"&key={self.census_api_key}"
        )
        async with session.get(full_url) as response:
            if response.status == 200:
                data = await response.json()
                naics_title = data[1][0] if len(data) > 1 else None
                return {"naics_code": naics_code, "naics_title": naics_title}
            else:
                print(f"Failed to fetch data for NAICS code {naics_code}: {response.status}")
                return {"naics_code": naics_code, "naics_title": None}

    async def _fetch_all_naics_data(
        self,
        naics_codes: List[str],
    ) -> List[Dict[str, Optional[str]]]:
        """Fetch data for multiple NAICS codes asynchronously using a shared session.

        Args:
            naics_codes (List[str]): A list of unique NAICS codes to fetch data for.

        Returns:
            List[Dict[str, Optional[str]]]: A list of dictionaries with `naics_code` and `naics_title`.
        """
        async with aiohttp.ClientSession() as session:  # Shared session for all requests
            tasks = [self._fetch_single_naics_data(code, session) for code in naics_codes]
            return await asyncio.gather(*tasks)

    def process_naics_codes(
        self,
        df: pd.DataFrame,
        code_column: str,
    ) -> pd.DataFrame:
        """Process NAICS codes in a DataFrame and return a DataFrame with fetched data.

        Args:
            df (pd.DataFrame): The DataFrame containing NAICS codes.
            code_column (str): The name of the column containing the NAICS codes.

        Returns:
            pd.DataFrame: A DataFrame containing `naics_code` and `naics_title`.
        """
        unique_naics_codes = df[code_column].unique().tolist()
        data = asyncio.run(self._fetch_all_naics_data(unique_naics_codes))
        result_df = pd.DataFrame(data)
        return result_df


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../conf",
        job_name="smoke-testing-census",
    ):
        cfg = hydra.compose(config_name="main")
        df = pd.DataFrame({"naics_code": ["481112"]})
        try:
            fetcher = NaicsDataFetcher(cfg)
            result_df = fetcher.process_naics_codes(df, "naics_code")
            print(result_df)
        except EnvironmentError as e:
            print(e)
