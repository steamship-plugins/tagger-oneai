import os
from typing import List

import pytest
from pydantic import ValidationError
from steamship import Block, DocTag, Steamship, SteamshipError
from steamship.data.file import File
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.service import PluginRequest

from src.api import OneAITaggerPlugin

__copyright__ = "Steamship"
__license__ = "MIT"

def test_plugin_fails_with_bad_config():
    # With no client, no config
    with pytest.raises(TypeError):
        # TODO: How do we ignore the PyCharm "parameter unfilled" error below?
        OneAITaggerPlugin()

    # With no config
    with pytest.raises(TypeError):
        # TODO: How do we ignore the PyCharm "parameter unfilled" error below?
        OneAITaggerPlugin(client=Steamship())

    # With None config
    with pytest.raises(SteamshipError):
        # TODO: How do we ignore the PyCharm "parameter not what was expected" error below?
        OneAITaggerPlugin(client=Steamship(), config=None)

    # With empty dict config
    with pytest.raises(SteamshipError):
        OneAITaggerPlugin(client=Steamship(), config=dict())

    valid_config = {
        "api_key": "foo",
        "input_type": "conversation",
        "skills": "foo"
    }

    # Missing a required config field
    for key in valid_config.keys():
        bad_config = valid_config.copy()
        del bad_config[key]
        with pytest.raises(ValidationError):
            OneAITaggerPlugin(client=Steamship(), config=bad_config)

    # Using a bad input_type
    bad_config = valid_config.copy()
    bad_config["input_type"] = "recording_of_dolphin_clicks"
    with pytest.raises(ValidationError):
        OneAITaggerPlugin(client=Steamship(), config=bad_config)
