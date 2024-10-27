# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for fetching NAICS codes associated with FRS registry IDs from the EPA's FRS API.

This module defines the `FrsDataFetcher` class, which uses asynchronous requests to query
the EPA's FRS API for unique `registry_id` values found in a given DataFrame and retrieve
associated `naics_code` values. The class handles duplicate `registry_id` entries, ensuring
each unique ID is queried only once. It also leverages asynchronous requests to improve
performance when querying multiple IDs.

Classes:
    FrsDataFetcher: Encapsulates methods for fetching NAICS code descriptions for FRS registry
                    IDs from the EPA's FRS API.

Functions:
    __init__(cfg: DictConfig): Initializes the `FrsDataFetcher` with a configuration object
                               containing API endpoint information.
    _fetch_single_frs_data(frs_registry_id: str, session: aiohttp.ClientSession) -> Dict[str, Optional[str]]:
        Asynchronously fetches data for a single FRS `registry_id`, returning the `naics_code`
        if the query is successful. If unsuccessful, the function returns `None` for the `naics_code`.
    _fetch_all_frs_data(registry_ids: List[str]) -> List[Dict[str, Optional[str]]]:
        Asynchronously fetches data for a list of unique `registry_id`s by creating tasks for
        each ID. Returns a list of dictionaries containing `registry_id` and `naics_code` values.
    process_registry_ids(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
        Processes a DataFrame containing `registry_id`s, extracts unique IDs, and fetches
        corresponding `naics_code` data using the FRS API. Constructs and returns a new DataFrame
        containing `registry_id` and `naics_code` columns. If a query fails, `naics_code` is set
        to `None`.

Example Usage:
    ```
    import hydra
    from omegaconf import DictConfig
    import pandas as pd

    # Load configuration using Hydra
    with hydra.initialize(config_path="."):
        cfg = hydra.compose(config_name="main")

    # Example DataFrame with FRS registry IDs
    df = pd.DataFrame({"registry_id": ["110002567277", "110002567278", "110002567279"]})

    # Create an instance of the FrsDataFetcher and fetch data
    fetcher = FrsDataFetcher(cfg)
    result_df = fetcher.process_registry_ids(df, "registry_id")
    print(result_df)
    ```

Notes:
    - Requires `aiohttp` for asynchronous HTTP requests and `omegaconf` for configuration handling.
    - Asynchronous requests allow concurrent API queries, enhancing performance, especially with large datasets.
    - Manages duplicate `registry_id`s by querying each unique ID only once, even if duplicates exist in the input DataFrame.
    - Configurable endpoints and query parameters through `DictConfig`, allowing flexibility for API changes.

"""


import asyncio
from typing import Dict, List, Optional

import aiohttp
import pandas as pd
from omegaconf import DictConfig


class FrsDataFetcher:
    """Class for fetching NAICS codes associated with FRS registry IDs from the EPA's FRS API."""

    def __init__(self, cfg: DictConfig):
        """Initialize the FrsDataFetcher with configuration.

        Args:
            cfg (DictConfig): The configuration object.

        """
        self.cfg = cfg
        self.base_url = cfg.frs_api.base_url

    async def _fetch_single_frs_data(
        self,
        frs_registry_id: str,
        session: aiohttp.ClientSession,
    ) -> Dict[str, Optional[str]]:
        """Fetch data for a single registry ID asynchronously using a shared session.

        Args:
            frs_registry_id (str): The FRS registry ID to fetch data for.
            session (aiohttp.ClientSession): The shared aiohttp session.

        Returns:
            Dict[str, Optional[str]]: A dictionary with `registry_id` and `naics_code`.

        """
        endpoint = (
            f"{self.cfg.frs_api.endpoints.frs_facility_site}/{self.cfg.frs_api.query_parameters.registry_id_equals}".format(
                frs_registry_id=frs_registry_id
            )
        )
        join_endpoint = f"{self.cfg.frs_api.query_parameters.join_type}/{self.cfg.frs_api.endpoints.frs_interest}/{self.cfg.frs_api.query_parameters.join_type}/{self.cfg.frs_api.endpoints.frs_naics}"
        primary_filter = f"{self.cfg.frs_api.query_parameters.primary_indicator_equals}/{self.cfg.frs_api.query_parameters.first_last}/{self.cfg.frs_api.query_parameters.format}"
        full_url = f"{self.base_url}/{endpoint}/{join_endpoint}/{primary_filter}"

        # Make the request using the shared session
        async with session.get(full_url) as response:
            if response.status == 200:
                data = await response.json()
                naics_code = data[0].get("naics_code") if data else None
                return {"registry_id": frs_registry_id, "naics_code": naics_code}
            else:
                print(f"Failed to fetch data for {frs_registry_id}: {response.status}")
                return {"registry_id": frs_registry_id, "naics_code": None}

    async def _fetch_all_frs_data(self, registry_ids: List[str]) -> List[Dict[str, Optional[str]]]:
        """Fetch data for multiple registry IDs asynchronously using a shared session.

        Args:
            registry_ids (List[str]): A list of unique FRS registry IDs to fetch data for.

        Returns:
            List[Dict[str, Optional[str]]]: A list of dictionaries with `registry_id` and `naics_code`.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_single_frs_data(reg_id, session) for reg_id in registry_ids]
            return await asyncio.gather(*tasks)

    def process_registry_ids(self, df: pd.DataFrame, id_column: str) -> pd.DataFrame:
        """Process registry IDs in a DataFrame and return a DataFrame with fetched data.

        Args:
            df (pd.DataFrame): The DataFrame containing FRS registry IDs.
            id_column (str): The name of the column containing the registry IDs.

        Returns:
            pd.DataFrame: A DataFrame containing `registry_id` and `naics_code`.
        """
        # Extract unique registry IDs from the specified column
        unique_registry_ids = df[id_column].unique().tolist()

        # Run the asynchronous fetch with a shared session
        data = asyncio.run(self._fetch_all_frs_data(unique_registry_ids))

        # Convert the result to a DataFrame
        result_df = pd.DataFrame(data)
        return result_df


if __name__ == "__main__":
    # This is only used for smoke testing
    import hydra

    with hydra.initialize(
        version_base=None,
        config_path="../../conf",
        job_name="smoke-testing-frs",
    ):
        cfg = hydra.compose(config_name="main")
        df = pd.DataFrame({"registry_id": [110000438893]})
        fetcher = FrsDataFetcher(cfg)
        result_df = fetcher.process_registry_ids(df, "registry_id")
        print(result_df)
