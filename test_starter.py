import unittest
from pathlib import Path


STARTER_DIRECTORY = Path(__file__).resolve().parent / "starter"


def load_tests(loader, standard_tests, pattern):
    """Include the starter project's tests in root-level discovery."""
    return loader.discover(
        str(STARTER_DIRECTORY),
        pattern=pattern,
        top_level_dir=str(STARTER_DIRECTORY),
    )
