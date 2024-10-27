# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Create table module.

This module handles the creation of a SQLite database and associated tables
for storing TRI (Toxics Release Inventory) data. It checks if the necessary
tables already exist and, if not, creates them based on the SQLAlchemy models
defined in the data models module.

Functions:
    create_database() -> sessionmaker:
        Creates the SQLite database and tables if they do not already exist.
        Returns a sessionmaker instance for connecting to and interacting with
        the database.

Usage:
    This module can be used to initialize the TRI database with a defined
    structure before querying or inserting data. It is designed to be
    idempotent, meaning running it multiple times will not recreate existing
    tables.

Example:
    # Initialize the database and get a sessionmaker
    Session = create_database()
    # Use the session to query or insert data
    with Session() as session:
        # Query, add, or commit data here

"""


import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from src.data_processing.data_models import Base


def create_database() -> sessionmaker:
    """Creates a SQLite database and tables for storing TRI data.

    Returns:
        sessionmaker: A sessionmaker object for connecting to the database.

    """
    current_dir = os.getcwd()
    db_path = os.path.join(
        current_dir,
        "data",
        "processed",
        "tri_eol_additives.sqlite",
    )
    DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(DATABASE_URL, echo=True)
    inspector = inspect(engine)

    # Check if the tables already exist
    existing_tables = inspector.get_table_names()
    if existing_tables:
        print("Tables already exist:", existing_tables)
    else:
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        print("SQLite database and tables created successfully!")

    Session = sessionmaker(bind=engine)
    return Session


if __name__ == "__main__":
    create_database()
