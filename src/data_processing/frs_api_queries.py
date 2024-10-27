# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for fetching NAICS codes from the EPA's Facility Registry Service (FRS) API.

This module contains functions to asynchronously query the EPA's FRS API for unique
`registry_id` values found in a given DataFrame, and to retrieve associated `naics_code`
values. The module is designed to handle duplicate `registry_id` entries, ensuring each
unique ID is queried only once, and uses asynchronous requests to improve efficiency.

Functions:
    fetch_single_frs_data(cfg: DictConfig, frs_registry_id: str) -> Dict[str, Optional[str]]:
        Asynchronously fetches data for a single FRS `registry_id` and retrieves the
        `naics_code` if the query is successful. Returns `None` for `naics_code` in case
        of an error.

    fetch_all_frs_data(cfg: DictConfig, registry_ids: List[str]) -> List[Dict[str, Optional[str]]]:
        Asynchronously fetches data for a list of unique `registry_id`s by creating
        tasks for each ID. Returns a list of dictionaries containing `registry_id` and
        `naics_code` values.

    process_registry_ids(cfg: DictConfig, df: pd.DataFrame, id_column: str) -> pd.DataFrame:
        Processes a DataFrame with `registry_id`s, extracts unique IDs, and fetches data
        using the FRS API. Constructs and returns a new DataFrame containing `registry_id`
        and `naics_code` columns. If a query fails, the `naics_code` is set to `None`.

Example Usage:
    Load configuration using Hydra, define a DataFrame with `registry_id` values, and use
    `process_registry_ids` to retrieve a DataFrame with fetched `naics_code` data.

Notes:
    - Requires `aiohttp` for asynchronous HTTP requests and `omegaconf` for configuration handling.
    - Asynchronous approach enables concurrent API requests for improved performance.
    - Handles duplicate `registry_id`s by querying each unique ID only once, even if duplicates
      exist in the input DataFrame.

"""


import asyncio
from typing import Dict, List, Optional

import aiohttp
import pandas as pd
from omegaconf import DictConfig


async def fetch_single_frs_data(
    cfg: DictConfig,
    frs_registry_id: str,
) -> Dict[str, Optional[str]]:
    """Fetch data for a single registry ID asynchronously.

    This function fetches data for a single FRS registry ID using an asynchronous
    GET request to the FRS API. It returns the `registry_id` and `naics_code` if
    successful, or `None` if unsuccessful.

    Args:
        cfg (DictConfig): The configuration object.
        frs_registry_id (str): The FRS registry ID to fetch data for.

    Returns:
        Dict[str, Optional[str]]: A dictionary with `registry_id` and `naics_code`.
    """
    # Construct the URL based on configuration and registry ID
    base_url = cfg.frs_api.base_url
    endpoint = f"{cfg.frs_api.endpoints.frs_facility_site}/{cfg.frs_api.query_parameters.registry_id_equals}".format(
        frs_registry_id=frs_registry_id
    )
    join_endpoint = f"{cfg.frs_api.query_parameters.join_type}/{cfg.frs_api.endpoints.frs_interest}/{cfg.frs_api.query_parameters.join_type}/{cfg.frs_api.endpoints.frs_naics}"
    primary_filter = f"{cfg.frs_api.query_parameters.primary_indicator_equals}/{cfg.frs_api.query_parameters.first_last}/{cfg.frs_api.query_parameters.format}"
    full_url = f"{base_url}/{endpoint}/{join_endpoint}/{primary_filter}"

    # Make an asynchronous GET request
    async with aiohttp.ClientSession() as session:
        async with session.get(full_url) as response:
            if response.status == 200:
                data = await response.json()
                naics_code = data[0].get("naics_code") if data else None
                return {"registry_id": frs_registry_id, "naics_code": naics_code}
            else:
                print(f"Failed to fetch data for {frs_registry_id}: {response.status}")
                return {"registry_id": frs_registry_id, "naics_code": None}


async def fetch_all_frs_data(
    cfg: DictConfig,
    registry_ids: List[str],
) -> List[Dict[str, Optional[str]]]:
    """Fetch data for multiple registry IDs asynchronously.

    Args:
        cfg (DictConfig): The configuration object.
        registry_ids (List[str]): A list of unique FRS registry IDs to fetch data for.

    Returns:
        List[Dict[str, Optional[str]]]: A list of dictionaries with `registry_id` and `naics_code`.
    """
    tasks = [fetch_single_frs_data(cfg, reg_id) for reg_id in registry_ids]
    return await asyncio.gather(*tasks)


def process_registry_ids(
    cfg: DictConfig,
    df: pd.DataFrame,
    id_column: str,
) -> pd.DataFrame:
    """Process registry IDs in a DataFrame and return a DataFrame with fetched data.

    This function processes a DataFrame containing FRS registry IDs and fetches data
    for each unique ID using the FRS API. The fetched data is then returned as a new
    DataFrame with `registry_id` and `naics_code`.

    Args:
        cfg (DictConfig): The configuration object.
        df (pd.DataFrame): The DataFrame containing FRS registry IDs.
        id_column (str): The name of the column containing the registry IDs.

    Returns:
        pd.DataFrame: A DataFrame containing `registry_id` and `naics_code`.
    """
    # Extract unique registry IDs from the specified column
    unique_registry_ids = df[id_column].unique().tolist()

    # Run the asynchronous fetch
    data = asyncio.run(fetch_all_frs_data(cfg, unique_registry_ids))

    # Convert the result to a DataFrame
    result_df = pd.DataFrame(data)
    return result_df
