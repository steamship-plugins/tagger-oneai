"""Steamship OneAI Tagger.

Enables you to tag the Blocks of a File using one or more OneAI skills.
"""

from typing import Any, Dict, List, Type

from steamship import Steamship
from steamship.app import Response, create_handler
from steamship.base.error import SteamshipError
from steamship.plugin.blockifier import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger

from oneai.api_spec import OneAIInputType
from oneai.client import OneAIClient


class OneAITaggerPluginConfig(Config):
    """Configuration required to instantiate a OneAI Tagger."""

    api_key: str
    skills: List[str]
    input_type: OneAIInputType

    def __init__(self, **kwargs):
        if isinstance(kwargs.get("skills"), str):
            kwargs["skills"] = kwargs["skills"].split(",")
        super().__init__(**kwargs)

    @property
    def steps(self):
        """Return a properly formatted list of steps for OneAI to perform from the list of skills."""
        return [{"skill": skill} for skill in self.skills]


class OneAITagger(Tagger):
    """A steamship tagger that uses OneAI skills."""

    def __init__(self, client: Steamship, config: Dict[str, Any]):
        super().__init__(client, config)

    def config_cls(self) -> Type[Config]:
        """Config object used to pass configuration to the API."""
        return OneAITaggerPluginConfig

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        """Tag the blocks inside a file using OneAI."""
        oneai_client = OneAIClient(api_key=self.config.api_key)
        if oneai_client is None:
            raise SteamshipError(
                message="Unable to create OneAIClient. "
                "Please make sure your plugin configuration contains a valid `api_key`."
            )

        file = request.data.file
        for block in file.blocks:
            # Create tags for that block via OneAI and add them
            if speaker_tags := [tag for tag in block.tags if tag.kind == "Speaker"]:
                text = [
                    {
                        "speaker": speaker_tag.name,
                        "utterance": block.text[speaker_tag.start_idx : speaker_tag.end_idx],
                    }
                    for speaker_tag in speaker_tags
                ]
                input_type = OneAIInputType.CONVERSATION
            else:
                text = block.text
                input_type = OneAIInputType.AUTO

            response = oneai_client.request(
                input=text,
                input_type=input_type,
                steps=self.config.steps,
            )
            if response:
                block.tags.extend(response.to_steamship_tags())

        return Response(data=BlockAndTagPluginOutput(file=file))


handler = create_handler(OneAITagger)
