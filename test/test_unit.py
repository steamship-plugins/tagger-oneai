"""Test OneAITagger via unit tests."""
import json
from test import INPUT_FILES, TEST_DATA
from test.utils import create_file, get_steamship_client

import pytest
from pydantic import ValidationError
from steamship import Steamship
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.service import PluginRequest

from src.api import OneAITagger


@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_tagger(input_file):
    """Test OneAI Tagger with structured and unstructured input data."""
    config = json.load((TEST_DATA / "config.json").open())

    client = get_steamship_client()
    tagger = OneAITagger(client=client, config=config)

    test_file = create_file(input_file)
    request = PluginRequest(data=BlockAndTagPluginInput(file=test_file))

    response = tagger.run(request)

    validate_response(response)


def validate_response(response):
    """Test the response of OneAI Tagger."""
    assert response.data is not None
    assert response.data.file is not None
    file = response.data.file
    validate_file(file)


def validate_file(file):
    """Validate the contents of a steamship File that is tagged using Steamship's OneAI Tagger."""
    assert len(file.blocks) == 1
    block = file.blocks[0]
    assert len(block.tags) > 0
    for tag in block.tags:
        if tag.kind != "Speaker":
            assert tag.kind in ("emotions", "dialogue-segmentation")
            assert tag.name.lower() in (
                "happiness",
                "sadness",
                "anger",
                "surprise",
                "fear",
                "dialogue-segment",
            )


def test_plugin_fails_with_bad_config():
    """Test if the creation of the OneAI Tagger fails when bad configuration is passed."""
    # With no client, no config
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        OneAITagger()

    # With no config
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        OneAITagger(client=Steamship())

    valid_config = {"api_key": "foo", "input_type": "conversation", "skills": "foo"}

    # Missing a required config field
    for key in valid_config.keys():
        bad_config = valid_config.copy()
        del bad_config[key]
        with pytest.raises(ValidationError):
            OneAITagger(client=Steamship(), config=bad_config)

    # Using a bad input_type
    bad_config = valid_config.copy()
    bad_config["input_type"] = "recording_of_dolphin_clicks"
    with pytest.raises(ValidationError):
        OneAITagger(client=Steamship(), config=bad_config)
