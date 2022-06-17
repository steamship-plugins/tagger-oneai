"""Test tagger-classification-hf-autotrain via unit tests."""

from steamship import Block, File
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.service import PluginRequest

from src.api import OneAITagger
from test.util import get_steamship_client

ENVIRONMENT = "test"

TEST_CONVERSATION = 'Prospect  0:36\nIf you Is it possible for you to call me on Friday by the time and have a look on the whole document which I have downloaded?\n\nAgent  0:40\nYeah , just give me a just shoot me an email with some availability for John, and then I can put something together ..\n\nProspect  0:49\nYeah, sure. I let me have a look into that. Actually, it sounded interesting to me, because we are also working on analytics next month.\n\nAgent  0:59\nOf course, yeah. What are some of the things that you guys are looking for? I know, I mean, carrot soup, just as people become more data mature, you know, it becomes so important for, for companies to understand, you know, volcano behavior of users. So, yeah, I\'d be happy to give you guys an overview. You want me to follow up like later this week? and then we can figure out, you know, timing is really like next week.\n\nProspect  1:44\nYeah, 1pm would be fine. Okay,\n\nAgent  1:46\ncool. Sounds good. Well, I\'ll go ahead and add you on Monday. So you can put a name to the face and if anything changes, just let me know. But otherwise, I\'ll look forward to talking to you again on Friday.\n\nProspect  1:56\nYeah.\n\nAgent  1:58\nOkay, cool. So if we need to move that we, you know, we can do that.\n\nProspect  1:56\nThanks, bye.\n'


def test_tagger():
    """Test HF AutoTrain Tagger without edge cases."""
    SKILL_TO_LABEL_TYPE = {
        # "dialogue-segmentation": "dialogue-segmentat",
        # "action-items": "action-items",
        "emotions": "Hapiness"
    }
    config = {
        "skills": ",".join(SKILL_TO_LABEL_TYPE.keys()),
        "input_type": 'auto-detect',
        "api_key": "84ae4e01-e565-4791-a30c-181534f3eef4"
    }
    client = get_steamship_client(ENVIRONMENT)
    tagger = OneAITagger(client=client, config=config)

    test_file = File(blocks=[Block(text=TEST_CONVERSATION)])
    request = PluginRequest(data=BlockAndTagPluginInput(file=test_file))

    response = tagger.run(request)

    assert response.data is not None

    assert response.data.file is not None
    file = response.data.file

    assert len(file.blocks) == 1
    block = file.blocks[0]

    assert len(block.tags) == 4
    for tag in block.tags:
        assert tag.kind in SKILL_TO_LABEL_TYPE.keys()
        assert tag.name in SKILL_TO_LABEL_TYPE.values()
