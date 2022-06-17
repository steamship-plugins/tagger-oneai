import pytest
from pydantic import ValidationError
from steamship import Steamship, SteamshipError

from src.api import OneAITagger

__copyright__ = "Steamship"
__license__ = "MIT"


def test_plugin_fails_with_bad_config():
    # With no client, no config
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        OneAITagger()

    # With no config
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        OneAITagger(client=Steamship())

    # With None config
    with pytest.raises(SteamshipError):
        # noinspection PyTypeChecker
        OneAITagger(client=Steamship(), config=None)

    # With empty dict config
    with pytest.raises(SteamshipError):
        OneAITagger(client=Steamship(), config=dict())

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
            OneAITagger(client=Steamship(), config=bad_config)

    # Using a bad input_type
    bad_config = valid_config.copy()
    bad_config["input_type"] = "recording_of_dolphin_clicks"
    with pytest.raises(ValidationError):
        OneAITagger(client=Steamship(), config=bad_config)
