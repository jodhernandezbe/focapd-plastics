# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Configuration module.

Module for defining configuration dataclasses to be used with Hydra for managing
and validating YAML-based configuration files.

This module contains dataclasses that represent the structure of an expected 
configuration file, which includes settings for various fields relevant to 
industry sectors, plastic additives, TRI (Toxics Release Inventory) files, 
and specific columns with associated attributes.

Classes:
    IndustrySector: Represents details about plastic-related industry sectors,
        including a description and NAICS codes.
    PlasticAdditives: Represents details about plastic additives, including a 
        description and TRI chemical identifiers.
    NeededColumn: Defines individual columns expected in TRI files, including 
        the column name and optional attributes, such as release type, 
        management type, and flags for specific categories (e.g., 
        hazardous waste, recycling).
    FileConfig: Encapsulates a list of NeededColumn entries, defining the 
        required columns for each TRI file.
    TriFiles: Represents all TRI file configurations, specifically organizing
        file_1a, file_1b, file_3a, and file_3c settings.
    MainConfig: Top-level configuration class aggregating the entire configuration 
        structure, including industry sectors, plastic additives, and TRI files.

This structure allows Hydra to load and manage hierarchical configurations 
efficiently, enabling clear validation and organized access to configuration data.

"""


from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IndustrySector:
    """Industry Sector."""
    description: str
    naics_code: List[str] = field(default_factory=list)


@dataclass
class PlasticAdditive:
    """Plastic Additives."""
    description: str
    tri_chem_id: List[str] = field(default_factory=list)


@dataclass
class NeededColumn:
    """Needed Column."""
    name: str
    relase_type: Optional[str] = None
    management_type: Optional[str] = None
    is_hazardous_waste: Optional[bool] = None
    is_landfilling: Optional[bool] = None
    is_recycling: Optional[bool] = None
    is_for_metals: Optional[bool] = None
    is_wastewater: Optional[bool] = None
    is_brokering: Optional[bool] = None
    is_incineration: Optional[bool] = None
    description: Optional[str] = None


@dataclass
class FileConfig:
    """File Configuration."""
    needed_columns: List[NeededColumn] = field(default_factory=list)


@dataclass
class TriFiles:
    """TRI Files."""
    file_1a: FileConfig
    file_1b: FileConfig
    file_3a: FileConfig
    file_3c: FileConfig


@dataclass
class MainConfig:
    """Main Configuration."""
    industry_sectors: IndustrySector
    plastics_additives: PlasticAdditive
    tri_files: TriFiles
