"""Test if we can properly parse OneAI responses."""
import json
import re
from pathlib import Path
from test import INPUT_FILES, TEST_DATA
from test.utils import get_oneai_client, read_test_input

import pytest

from oneai.api_spec import OneAIInputType, OneAISkill


@pytest.mark.parametrize("input_file", INPUT_FILES)
def test_response_parsing(input_file: Path) -> None:
    """Test if we can properly parse OneAI responses."""
    config = json.load((TEST_DATA / "config.json").open())
    oneai_client = get_oneai_client(config["api_key"])
    oneai_response = oneai_client.request(
        input=read_test_input(input_file),
        input_type=OneAIInputType.AUTO
        if input_file.suffix == ".txt"
        else OneAIInputType.CONVERSATION,
        steps=[{"skill": OneAISkill.EMOTIONS}],
    )
    assert oneai_response.output is not None
    assert len(oneai_response.output) == 1

    output_block = oneai_response.output[0]
    assert len(output_block.labels) > 0

    for label in output_block.labels:
        tag = label.to_steamship_tag()
        assert tag.kind is not None
        assert tag.name is not None
        if tag.value is not None:
            assert isinstance(tag.value, dict)
        if len(label.span) > 0:
            assert tag.start_idx is not None
            assert tag.end_idx is not None

        # Assert that the labels all perfectly capture text.
        label = oneai_response.input_text[tag.start_idx : tag.end_idx]
        assert not label.startswith(" ")
        assert not label.endswith(" ")

        # This is an indirect way to make sure that OneAI is, like us, start-inclusive and end-exclusive in their
        # indexing scheme (Python slice semantics) -- we test the ACTUAL character underneath the end_idx and verify
        # that it is a whitespace or punctuation character (which, for this test dataset, should hold).
        if tag.end_idx < len(oneai_response.input_text):
            assert re.findall(r"\W$", oneai_response.input_text[tag.end_idx])
