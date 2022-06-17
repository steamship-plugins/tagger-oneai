import logging
import os
from pathlib import Path

from steamship import Steamship

from src.utils.oneai import *


def get_steamship_client(environment: str) -> Steamship:
    return Steamship(profile=environment)


def get_oneai_client(key: str = None):
    if key is not None:
        return OneAIClient(key=key)
    environ_key = os.environ.get('ONEAI_KEY')
    if environ_key is not None:
        return OneAIClient(key=environ_key)
    logging.error("No OneAI key found. Please set ONEAI_KEY")
    return None


def read_test_file(filename: str):
    test_data_folder = Path(__file__).parent.parent / "test_data" / "inputs"
    with (test_data_folder / filename).open() as f:
        return f.read()
