"""Test tagger-classification-hf-autotrain via integration tests."""
import json
from test import INPUT_FILES, TEST_DATA
from test.test_unit import validate_file, validate_response
from test.utils import create_file, get_steamship_client

import pytest
from steamship import File, Plugin, PluginInstance

ENVIRONMENT = "staging"
TAGGER_HANDLE = "oneai-tagger"


def _get_plugin_instance(config) -> PluginInstance:
    client = get_steamship_client(ENVIRONMENT)

    plugin = Plugin.get(client, TAGGER_HANDLE).data
    assert plugin is not None
    assert plugin.id is not None
    plugin_instance = PluginInstance.create(
        client,
        plugin_handle=TAGGER_HANDLE,
        upsert=False,
        plugin_id=plugin.id,
        config=config,
    ).data
    assert plugin_instance is not None
    assert plugin_instance.id is not None
    return plugin_instance


@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_tagger_stateless(input_file):
    """Test the HF AutoTrain Classifier in a stateless way."""
    config = json.load((TEST_DATA / "config.json").open())

    tagger = _get_plugin_instance(config=config)

    tag_result = tagger.tag(doc=create_file(input_file))

    tag_result.wait()
    validate_response(tag_result)


@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_tagger_stateful(input_file):
    """Test the HF AutoTrain Classifier in a stateful way."""
    client = get_steamship_client(ENVIRONMENT)
    config = json.load((TEST_DATA / "config.json").open())

    tagger = _get_plugin_instance(config=config)

    # First we all the files in the space
    files = File.list(client).data.files
    for file in files:
        file.delete()

    # Then we check if it is really empty
    assert len(File.query(client, "blocktag").data.files) == 0
    assert len(File.query(client, 'blocktag and kind "Speaker"').data.files) == 0
    assert len(File.query(client, 'blocktag and kind "dialogue-segmentation"').data.files) == 0
    assert len(File.query(client, 'blocktag and name "dialogue-segment"').data.files) == 0
    assert len(File.query(client, 'blocktag and kind "emotions"').data.files) == 0

    file = create_file(input_file, client)
    file.tag(plugin_instance=tagger.handle).wait()
    file = file.refresh().data

    if input_file.suffix == ".json":
        assert len(File.query(client, 'blocktag and kind "Speaker"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "dialogue-segmentation"').data.files) == 1
    assert len(File.query(client, 'blocktag and name "dialogue-segment"').data.files) == 1
    assert len(File.query(client, 'blocktag and kind "emotions"').data.files) == 1

    if "sales_call" in input_file.name:
        assert (
            len(
                File.query(
                    client,
                    'blocktag and (kind "emotions" and name "anger") '
                    'and sameblock {kind "emotions" and name "sadness"}',
                ).data.files
            )
            == 1
        )
    else:
        assert (
            len(
                File.query(
                    client,
                    'blocktag and (kind "emotions" and name "happiness") '
                    'and sameblock {kind "emotions" and name "anger"} '
                    'and sameblock {kind "emotions" and name "surprise"} '
                    'and sameblock {kind "emotions" and name "sadness"}',
                ).data.files
            )
            == 1
        )

    validate_file(file)
