"""Steamship OneAI Plugin
"""

from typing import List, Type, Dict, Any

from pydantic import validator
from steamship import Block, Steamship
from steamship.app import App, create_handler, Response
from steamship.base.error import SteamshipError
from steamship.data.file import File
from steamship.plugin.blockifier import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger

from src.oneai import OneAIRequest, OneAIClient, OneAIInputType


class OneAITaggerPluginConfig(Config):
    api_key: str  # TODO: Ensure this is hard-checked to be not none
    skills: List[str]
    input_type: str

    def __init__(self, **kwargs):
        if isinstance(kwargs.get("skills", None), str):
            kwargs["skills"] = kwargs["skills"].split(",")
        super().__init__(**kwargs)

    @validator('input_type')
    def input_type_must_be_valid(cls, v):
        if v not in [OneAIInputType.conversation, OneAIInputType.article]:
            raise ValueError(f'must be either {OneAIInputType.conversation} or {OneAIInputType.article}')
        return v

    def step_list(self):
        """Return the list of steps for OneAI to perform, formatted for its API"""
        return [{"skill": skill} for skill in self.skills]


class OneAITaggerPlugin(Tagger, App):
    def __init__(self, client: Steamship, config: Dict[str, Any]):
        super().__init__(client, config)

        # This plugin requires configuration
        if self.config is None:
            raise SteamshipError(message="Missing Plugin Instance configuration dictionary.")

    def config_cls(self) -> Type[OneAITaggerPluginConfig]:
        return OneAITaggerPluginConfig

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> BlockAndTagPluginOutput:

        # TODO: Ensure base Tagger class checks to make sure this is not None
        file = request.data.file

        client = OneAIClient(key=self.config.api_key)
        if client is None:
            raise SteamshipError(
                message="Unable to create OneAIClient. Please make your plugin configuration contained a valid `api_key`.")

        output = BlockAndTagPluginOutput(file=File.CreateRequest())

        for block in request.data.file.blocks:
            # Create an output block for this block
            output_block = Block.CreateRequest(id=block.id)

            # Create tags for that block via  OneAI and add them
            request = OneAIRequest(
                text=block.text,
                input_type=self.config.input_type,
                steps=self.config.step_list()
            )
            response = client.request(request)
            if response:
                output_block.tags = response.to_tags()

            # Attach the output block to the response
            output.file.blocks.append(output_block)

        return output


handler = create_handler(OneAITaggerPlugin)
