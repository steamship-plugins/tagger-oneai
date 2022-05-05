"""Steamship OneAI Plugin
"""
import dataclasses
from typing import List

from steamship import Block, DocTag, Tag
from steamship.app import App, post, create_handler, Response
from steamship.plugin.tagger import Tagger
from steamship.plugin.service import PluginResponse, PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
import re
from steamship.base.error import SteamshipError
from steamship.data.file import File
from src.oneai import OneAIRequest, OneAIClient, OneAIInputType

class OneAITaggerPlugin(Tagger, App):
    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> PluginResponse[BlockAndTagPluginOutput]:
        if request is None:
            raise SteamshipError(message="Missing PluginRequest")

        if request.data is None:
            raise SteamshipError(message="Missing PluginRequest")

        if request.data.file is None:
            raise SteamshipError(message="Missing `file` field in PluginRequest")

        file = request.data.file

        if self.config is None:
            raise SteamshipError(message="Missing Plugin Instance configuration dictionary.")

        apikey = self.config.get('apikey', None)
        if apikey is None:
            raise SteamshipError(message="Missing `apikey` value in config. Please provide a OneAI API Key")

        skills = self.config.get('skills', None)
        if skills is None:
            raise SteamshipError(message="Missing `skills` value in config. Please provide a comma-separated list of OneAI tagging skills.")
        skills_list = map(lambda x: x.strip, skills.split(","))

        input_type = self.config.get('input_type', None)
        if input_type is None:
            raise SteamshipError(message="Missing `input_type` value in config. Please provide an input_type of either `article` or `conversation`.")
        if input_type not in [OneAIInputType.conversation, OneAIInputType.article]:
            raise SteamshipError(message="Invalide `input_type` value of {}. Please provide an input_type of either `article` or `conversation`.".format(input_type))

        client = OneAIClient(key=apikey)
        if client is None:
            raise SteamshipError(message="Unable to create OneAIClient. Please check to make sure the provided `apikey` config property was valid")

        output = BlockAndTagPluginOutput(file=File.CreateRequest())

        for block in request.data.file.blocks:
            request = OneAIRequest(
                text=block.text,
                input_type=input_type,
                steps=list(map(lambda skill: {"skill": skill}, skills_list))
            )
            response = client.request(request)
            tags = []
            if response and response.output and response.output[0]:
                for label in response.output[0].labels:
                    tags.append(label.to_steamship_tag())
            output.file.blocks.append(
                Block.CreateRequest(
                    id=block.id,
                    tags=tags
                )
            )

        return PluginResponse(data=output)

    @post('tag')
    def parse(self, **kwargs) -> dict:
        parseRequest = Tagger.parse_request(request=kwargs)
        parseResponse = self.run(parseRequest)
        return Tagger.response_to_dict(parseResponse)


handler = create_handler(OneAITaggerPlugin)
