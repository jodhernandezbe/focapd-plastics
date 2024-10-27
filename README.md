
# FOCAPD SI

## Overview

This repository contains the code to generate discrete distribution based on TRI data, as part of the FOCAPD 2024 Special Issue invitation.

## Requirements

1. Python >=3.12, <3.13
2. Poetry

## Poetry

### New Dependencies

When adding or updating dependencies, run `poetry add` or `poetry update` and commit the changes.

### pull

When pulling the latest changes, run the following command to ensure that your local environment matches the project's dependencies.

```
poetry install
```

### Run Commands

To execute commands inside the project's environment, use `run` as follows:

```
poetry run python src/main.py
```

Additionally, you can activate the virtual environment by running the following command:

```
poetry shell
```

## Pre-commit

### Changes

If there is any change in `.pre-commit-config.yaml`, the following command has to be run:

```
poetry run pre-commit autoupdate
```

### Pull

Each time you pull changes, run the following command to ensure your local environment is up-to-date:

```
poetry run pre-commit install
```

### Manually Run Hooks

To manually run all pre-commit hooks on all files in the repository, use the following command:

```
poetry run pre-commit run --all-files
```

Note: this is not required when you commit changes.

If you are running the above command or committing your changes, and one or more hooks like black or isort fail, stage their modifications to the git staging area by running `git add`. After that, you can run `commit` again.

### Installing pyright language server for IDE typecheck highlighting

Detailed instructions: https://microsoft.github.io/pyright/#/installation

[Pycharm](https://github.com/InSyncWithFoo/pyright-langserver-for-pycharm)

VSCode: search for `Pylance` on marketplace

Add path to executable to plugin:

```shell
which pyright-langserver
```

Insert that path to plugin config in your IDE as path to executable

## Documentation Style

The project follows the Google style to document the code. The pre-commit hooks are configured to check this style.

## Census Bureau Data:

Get your API key in: https://api.census.gov/data/key_signup.html


## U.S. EPA's Envirofacts

API documentation: https://www.epa.gov/enviro/envirofacts-data-service-api-v1
