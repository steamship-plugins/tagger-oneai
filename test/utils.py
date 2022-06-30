"""Collection of helper functions to support testing."""
import json
import os
from pathlib import Path
from typing import Optional

from steamship import Block, File, Steamship, Tag
from steamship.base import Client

from src.oneai.client import OneAIClient


def get_steamship_client(environment: str = "test") -> Steamship:
    """Get steamship client."""
    return Steamship(profile=environment)


def get_oneai_client(api_key: str = None) -> OneAIClient:
    """Instantiate a OneAIClient.

    The api_key should be passed as a parameter or be stored in the ONEAI_API_KEY environment variable.
    """
    api_key = api_key or os.environ.get("ONEAI_API_KEY")
    if api_key is not None:
        return OneAIClient(api_key=api_key)
    raise RuntimeError("No OneAI key found. Please set ONEAI_KEY")


def read_test_input(file: Path):
    """Read the contents of a file that contains text input."""
    with file.open() as f:
        text = f.read()
        return json.loads(text) if file.suffix == ".json" else text


def create_file(file_path: Path, client: Optional[Client] = None):
    """Create a steamship File by reading the contents of an input file."""
    input = read_test_input(file_path)
    if isinstance(input, list):
        tags = []
        text = []
        previous_end_idx = 0
        for message in input:
            utterance = message["utterance"]
            tags.append(
                Tag.CreateRequest(
                    kind="Speaker",
                    name=message["speaker"],
                    start_idx=previous_end_idx,
                    end_idx=previous_end_idx + len(utterance),
                )
            )
            previous_end_idx += len(utterance) + 1
            text.append(utterance)
    else:
        text = [input]
        tags = []
    if client:
        return File.create(
            client, blocks=[Block.CreateRequest(text=" ".join(text), tags=tags)]
        ).data
    else:
        return File(blocks=[Block(text=" ".join(text), tags=tags)])
