import dataclasses
from enum import Enum
from typing import List, Optional, Dict

import requests
from pydantic import BaseModel
from steamship import SteamshipError
from steamship.data.tags.tag import Tag


class OneAIInputType(str, Enum):
    article = "article"
    conversation = "conversation"
    auto_detect = "auto-detect"


@dataclasses.dataclass
class OneAIRequest:
    text: str
    input_type: OneAIInputType
    steps: List[Dict[str, str]]


class OneAITagSkill(str, Enum):
    emotions = "emotions"
    entities = "entities"
    keywords = "keywords"
    highlights = "highlights"


class OneAIStatus:
    success = "success"


class OneAiOutputLabel(BaseModel):
    type: Optional[str]
    name: Optional[str]
    skill: Optional[str]
    span: Optional[List[int]]
    span_text: Optional[str]
    data: Optional[dict]

    def to_steamship_tag(self) -> Optional[Tag.CreateRequest]:
        return Tag.CreateRequest(
            kind=self.skill,
            name=self.name or self.type,
            start_idx=self.span[0] if len(self.span) == 2 else None,
            end_idx=self.span[1] if len(self.span) == 2 else None,
            value=self.data
        )


class OneAiOutputBlock(BaseModel):
    block_id: Optional[str]
    generating_step: Optional[str]
    origin_block: Optional[str]
    origin_span: Optional[List[int]]
    text: Optional[str]
    labels: Optional[List[OneAiOutputLabel]]


class OneAiResponse(BaseModel):
    input_text: str
    status: str
    error: Optional[str] = None
    output: Optional[List[OneAiOutputBlock]] = None

    def to_tags(self) -> List[Tag.CreateRequest]:
        tags: List[Tag.CreateRequest] = []
        if self.output:
            for output in self.output:
                for label in output.labels:
                    tags.append(label.to_steamship_tag())
        return tags


def one_ai_label_to_steamship_tag(label: OneAiOutputLabel) -> Optional[Tag.CreateRequest]:
    return Tag.CreateRequest(
        kind=label.skill,
        name=label.type,
        start_idx=label.span[0] if len(label.span) == 2 else None,
        end_idx=label.span[1] if len(label.span) == 2 else None,
        value=label.data
    )


class OneAIClient:
    API_URL = "https://api.oneai.com/api/v0/pipeline"

    def __init__(self, key: str):
        self.api_key = key

    def request(self, request: OneAIRequest) -> OneAiResponse:
        """Performs a OneAI request. Throw a SteamshipError in the event of error or empty response.

        See: https://www.oneai.com/docs
        """

        # Note: varied casing in these header names shouldn't matter, but it's in their docs, so we'll stick with it.
        headers = {
            "api-key": self.api_key,
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        request_dict = dataclasses.asdict(request)
        response = requests.post(
            url=self.API_URL,
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
            ret = OneAiResponse(**response_dict)
            if not ret:
                raise SteamshipError(
                    message="Request from OneAI could not be interpreted as a OneAIResponse object."
                )
            return ret
        except Exception as ex:
            raise SteamshipError(
                message="Request from OneAI could not be interpreted as a OneAIResponse object. Exception: {}".format(
                    ex),
                error=ex
            )
