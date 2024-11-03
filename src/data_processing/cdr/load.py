# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for loading CDR data into a SQLite database.

This module defines the `CdrDataLoader` class, which is responsible for loading
various types of CDR (Chemical Data Reporting) data into a SQLite database. It extends
the `BaseDataLoader` class to utilize common data loading methods and provides
specialized methods for loading consumer and industrial use data.

Classes:
    CdrDataLoader: A class that provides methods to load cleaned CDR data into
        corresponding database tables. This class caches certain data to optimize
        database lookups and inserts.

Attributes:
    config (DictConfig): Configuration object containing application settings.
    session (Session): SQLAlchemy session for interacting with the database.
    cache_* (Dict[Tuple, int]): Caches for storing the IDs of various data models
        to reduce repeated database queries.

Methods:
    __init__(self, config: DictConfig, session: Session):
        Initializes the `CdrDataLoader` instance with the given configuration and session.

    _load_use(self, df: pd.DataFrame) -> pd.DataFrame:
        Loads general use data and assigns IDs for related records such as additives
        and industry sectors.

    _get_consumer_commercial_product_category(self, consumer_commercial_product_category: Union[str, None]) -> Union[int, None]:
        Fetches or creates a `ConsumerCommercialProductCategory` record and returns its ID.

    _get_consumer_commercial_function_category(self, consumer_commercial_function_category: Union[str, None]) -> Union[int, None]:
        Fetches or creates a `ConsumerCommercialFunctionCategory` record and returns its ID.

    _get_industry_function_category(self, industry_function_category: Union[str, None]) -> Union[int, None]:
        Fetches or creates an `IndustryFunctionCategory` record and returns its ID.

    _get_industry_use_sector_id(self, industry_sector_code: Union[str, None], industry_sector_name: Union[str, None]) -> Union[int, None]:
        Fetches or creates an `IndustryUseSector` record and returns its ID.

    _get_industrial_type_of_process_or_use(self, industrial_type_of_process_or_use: Union[str, None]) -> Union[int, None]:
        Fetches or creates an `IndustrialTypeOfProcessOrUse` record and returns its ID.

    load_commercial_and_consumer_use(self, df: pd.DataFrame):
        Loads a DataFrame containing consumer and commercial use data into the database.

    load_industrial_use(self, df: pd.DataFrame):
        Loads a DataFrame containing industrial use data into the database.

    _load_industry_use_sector_naics(self, df: pd.DataFrame):
        Loads `IndustryUseSectorNaics` data into the database using an enriched DataFrame.

Usage:
    The `CdrDataLoader` class is used for transforming and loading CDR data from
    DataFrames into the database. It ensures that related records are fetched or
    created as needed, optimizing the insertion process with caching mechanisms.

Example:
    >>> from sqlalchemy.orm import sessionmaker
    >>> from omegaconf import OmegaConf
    >>> config = OmegaConf.load("config.yaml")
    >>> session = sessionmaker(bind=engine)()
    >>> loader = CdrDataLoader(config, session)
    >>> loader.load_commercial_and_consumer_use(df_consumer)
    >>> loader.load_industrial_use(df_industrial)
"""


from typing import Dict, Tuple, Union

import pandas as pd
from omegaconf import DictConfig
from sqlalchemy.orm import Session

from src.data_processing.base import BaseDataLoader
from src.data_processing.data_models import (
    ConsumerCommercialFunctionCategory,
    ConsumerCommercialProductCategory,
    ConsumerCommercialUse,
    IndustrialTypeOfProcessOrUse,
    IndustrialUse,
    IndustryFunctionCategory,
    IndustryUseSector,
    IndustryUseSectorNaics,
)


class CdrDataLoader(BaseDataLoader):
    """Class for loading CDR data from a CSV file into a SQLite database.

    This class provides methods for loading CDR data from a CSV file into a SQLite
    database. It extends the `BaseDataLoader` class, which provides common data
    loading functionality.

    """

    def __init__(
        self,
        config: DictConfig,
        session: Session,
    ):
        super().__init__(config, session)
        self.cache_industry_sector_id: Dict[Tuple, int] = {}
        self.cache_industry_use_sector_id: Dict[Tuple, int] = {}
        self.cache_chemical_activity_id: Dict[Tuple, int] = {}
        self.cache_industrial_type_of_process_or_use_id: Dict[Tuple, int] = {}
        self.cache_industry_function_category_id: Dict[Tuple, int] = {}
        self.cache_consumer_commercial_product_category_id: Dict[Tuple, int] = {}
        self.cache_consumer_commercial_function_category_id: Dict[Tuple, int] = {}
        self.cache_additive_id: Dict[Tuple, int] = {}

    def _load_use(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        df["additive_id"] = df["casrn"].apply(
            lambda row: self._cache_get_or_create(
                self.cache_additive_id,
                self._get_additive_id,
                tri_chem_id=row,
            ),
        )
        df["industry_sector_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_industry_sector_id,
                        self._get_industry_sector_id,
                        **{
                            "naics_code": row["naics_code"],
                            "naics_title": row["naics_title"],
                        },
                    )
                )
                if pd.notnull(row["naics_code"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        return df

    def _get_consumer_commercial_product_category(
        self,
        consumer_commercial_product_category: Union[str, None],
    ):
        """Fetch a ConsumerCommercialProductCategory and return its id."""
        if consumer_commercial_product_category:
            product_category = self.get_or_create(
                ConsumerCommercialProductCategory,
                name=consumer_commercial_product_category,
            )
            return product_category.id
        return None

    def _get_consumer_commercial_function_category(
        self,
        consumer_commercial_function_category: Union[str, None],
    ):
        """Fetch a ConsumerCommercialFunctionCategory and return its id."""
        if consumer_commercial_function_category:
            function_category = self.get_or_create(
                ConsumerCommercialFunctionCategory,
                name=consumer_commercial_function_category,
            )
            return function_category.id
        return None

    def _get_industry_function_category(
        self,
        industry_function_category: Union[str, None],
    ):
        """Fetch an IndustryFunctionCategory and return its id."""
        if industry_function_category:
            function_category = self.get_or_create(
                IndustryFunctionCategory,
                name=industry_function_category,
            )
            return function_category.id
        return None

    def _get_industry_use_sector_id(
        self,
        industry_sector_code: Union[str, None],
        industry_sector_name: Union[str, None],
    ):
        """Fetch an IndustryUseSector and return its id."""
        if industry_sector_code and industry_sector_name:
            sector = self.get_or_create(
                IndustryUseSector,
                code=industry_sector_code,
                name=industry_sector_name,
            )
            return sector.id
        return None

    def _get_industrial_type_of_process_or_use(
        self,
        industrial_type_of_process_or_use: Union[str, None],
    ):
        """Fetch an IndustrialTypeOfProcessOrUse and return its id."""
        if industrial_type_of_process_or_use:
            process_or_use = self.get_or_create(
                IndustrialTypeOfProcessOrUse,
                name=industrial_type_of_process_or_use,
            )
            return process_or_use.id
        return None

    def load_commercial_and_consumer_use(
        self,
        df: pd.DataFrame,
    ):
        """Load a DataFrame with cleaning commercial and consumer use data.

        Args:
            df (pd.DataFrame): DataFrame containing commercial and consumer use data.
        """
        df = self._load_use(df)
        df["product_category_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_consumer_commercial_product_category_id,
                        self._get_consumer_commercial_product_category,
                        consumer_commercial_product_category=row["consumer_commercial_product_category"],
                    )
                )
                if pd.notnull(row["consumer_commercial_product_category"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        df["function_category_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_consumer_commercial_function_category_id,
                        self._get_consumer_commercial_function_category,
                        consumer_commercial_function_category=row["consumer_commercial_function_category"],
                    )  # type: ignore [reportCallIssue]
                )
                if pd.notnull(row["consumer_commercial_function_category"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )

        insert_df = df[
            [
                "product_category_id",
                "function_category_id",
                "additive_id",
                "percentage",
                "type_of_use",
                "industry_sector_id",
            ]
        ]
        insert_df.to_sql(
            name=ConsumerCommercialUse.__tablename__,
            con=self.session.get_bind(),
            if_exists="append",
            index=False,
            method="multi",
            chunksize=200,
        )
        self.session.commit()

    def load_industrial_use(
        self,
        df: pd.DataFrame,
    ):
        """Load industrial use data into the database.

        Args:
          df (pd.DataFrame): DataFrame containing industrial use data.
        """
        df = self._load_use(df)
        df["industrial_type_of_process_or_use_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_industrial_type_of_process_or_use_id,
                        self._get_industrial_type_of_process_or_use,
                        industrial_type_of_process_or_use=row["industrial_type_of_process_or_use"],
                    )
                )
                if pd.notnull(row["industrial_type_of_process_or_use"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        df["industry_function_category_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_industry_function_category_id,
                        self._get_industry_function_category,
                        industry_function_category=row["industry_function_category"],
                    )
                )
                if pd.notnull(row["industry_function_category"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        df["industry_use_sector_id"] = df.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_industry_use_sector_id,
                        self._get_industry_use_sector_id,
                        industry_sector_code=row["industry_sector_code"],
                        industry_sector_name=row["industry_sector_name"],
                    )
                )
                if pd.notnull(row["industry_sector_code"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        insert_df = df[
            [
                "industrial_type_of_process_or_use_id",
                "industry_function_category_id",
                "additive_id",
                "percentage",
                "industry_sector_id",
                "industry_use_sector_id",
            ]
        ]
        insert_df.to_sql(
            name=IndustrialUse.__tablename__,
            con=self.session.get_bind(),
            if_exists="append",
            index=False,
            method="multi",
            chunksize=200,
        )

        self._load_industry_use_sector_naics(df)

        self.session.commit()

    def _load_industry_use_sector_naics(
        self,
        df: pd.DataFrame,
    ):
        """Load IndustryUseSectorNaics data."""
        df_record = df[
            [
                "industrial_use_naics_code",
                "industrial_use_naics_title",
                "industry_use_sector_id",
            ]
        ]
        df_record = df_record.dropna(subset=["industry_use_sector_id"])  # type: ignore [reportCallIssue]
        df_record = df_record.drop_duplicates()
        df_record["industry_sector_id"] = df_record.apply(
            lambda row: (
                (
                    self._cache_get_or_create(
                        self.cache_industry_sector_id,
                        self._get_industry_sector_id,
                        **{
                            "naics_code": row["industrial_use_naics_code"],
                            "naics_title": row["industrial_use_naics_title"],
                        },
                    )
                )
                if pd.notnull(row["industrial_use_naics_code"])
                else None
            ),  # type: ignore [reportCallIssue]
            axis=1,
        )
        insert_df = df_record[["industry_sector_id", "industry_use_sector_id"]]
        insert_df.to_sql(
            name=IndustryUseSectorNaics.__tablename__,
            con=self.session.get_bind(),
            if_exists="append",
            index=False,
            method="multi",
            chunksize=200,
        )
