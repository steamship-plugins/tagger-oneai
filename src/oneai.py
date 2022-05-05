import dataclasses
import json

import requests
from typing import List, Optional

from steamship import SteamshipError
from steamship.data.tags.tag import Tag


@dataclasses.dataclass
class OneAIRequest:
    text: str
    input_type: str
    steps: List[dict]


class OneAITagSkill:
    emotions = "emotions"
    entities = "entities"
    keywords = "keywords"
    highlights = "highlights"


class OneAIInputType:
    article = "article"
    conversation = "conversation"


class OneAIStatus:
    success = "success"


@dataclasses.dataclass
class OneAiOutputLabel:
    type: str
    name: str
    span: List[int]
    span_text: str
    data: dict

    @staticmethod
    def from_dict(d: dict) -> Optional["OneAiOutputLabel"]:
        if d is None:
            return None

        return OneAiOutputLabel(
            type = d.get("type", None),
            name=d.get("name", None),
            span=d.get("span", None),
            span_text=d.get("span_text", None),
            data=d.get("data", None)
        )

    def to_steamship_tag(self) -> Optional[Tag.CreateRequest]:
        if not self.span or len(self.span) != 2:
            return None

        return Tag.CreateRequest(
            kind=self.type,
            name=self.name,
            startIdx=self.span[0], # Safe because of check above
            endIdx=self.span[1], # Safe because of check above
            value=self.data
        )

@dataclasses.dataclass
class OneAiOutputBlock:
    block_id: str
    generating_step: str
    origin_block: str
    origin_span: List[int]
    text: str
    labels: List[OneAiOutputLabel]

    @staticmethod
    def from_dict(d: dict) -> Optional["OneAiOutputBlock"]:
        if d is None:
            return None

        return OneAiOutputBlock(
            block_id = d.get("block_id", None),
            generating_step=d.get("generating_step", None),
            origin_block=d.get("origin_block", None),
            origin_span=d.get("origin_span", None),
            text=d.get("text", None),
            labels=[OneAiOutputLabel.from_dict(l) for l in d.get("labels", [])]
        )


@dataclasses.dataclass
class OneAiResponse:
    input_text: str
    status: str
    error: str
    output: List[OneAiOutputBlock]

    @staticmethod
    def from_dict(d: dict) -> Optional["OneAiResponse"]:
        if d is None:
            return None

        return OneAiResponse(
            input_text = d.get("input_text", None),
            status=d.get("status", None),
            error=d.get("error", None),
            output=[OneAiOutputBlock.from_dict(b) for b in d.get("output", [])]
        )



class OneAIClient:
    URL = "https://api.oneai.com/api/v0/pipeline"

    def __init__(self, key: str):
        self.key = key

    def request(self, request: OneAIRequest) -> OneAiResponse:
        """Performs a OneAI request. Throw a SteamshipError in the event of error or empty response.

        See: https://www.oneai.com/docs
        """

        # Note: varied casing in these header names shouldn't matter, but it's in their docs, so we'll stick with it.
        headers = {
            "api-key": self.key,
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        request_dict = dataclasses.asdict(request)
        response = requests.post(
            url=OneAIClient.URL,
            headers=headers,
            json=request_dict,
        )

        if not response.ok:
            raise SteamshipError(
                message="Request to OneAI failed. Code={}. Body={}".format(response.status_code, response.text)
            )

        response_dict = response.json()
        if not response_dict:
            raise SteamshipError(
                message="Request from OneAI could not be interpreted as JSON."
            )

        try:
            ret = OneAiResponse.from_dict(response_dict)
            if not ret:
                raise SteamshipError(
                    message="Request from OneAI could not be interpreted as a OneAIResponse object."
                )
            return ret
        except Exception as ex:
            raise SteamshipError(
                message="Request from OneAI could not be interpreted as a OneAIResponse object. Exception: {}".format(ex),
                error=ex
            )

