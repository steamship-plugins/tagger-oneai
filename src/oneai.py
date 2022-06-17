import dataclasses
from typing import List, Optional, cast

import requests
from steamship import SteamshipError
from steamship.data.tags.tag import Tag
from typing import TypedDict


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

class OneAiOutputLabel(TypedDict):
    type: Optional[str]
    name: Optional[str]
    skill: Optional[str]
    span: Optional[List[int]]
    span_text: Optional[str]
    data: Optional[dict]


def one_ai_label_to_steamship_tag(label: OneAiOutputLabel) -> Optional[Tag.CreateRequest]:
    if len(label.get("span", [])) != 2:
        return None
    return Tag.CreateRequest(
        kind=label["skill"],
        name=label["type"],
        start_idx=label["span"][0],
        end_idx=label["span"][1],
        value=label["data"]
    )


class OneAiOutputBlock(TypedDict):
    block_id: Optional[str]
    generating_step: Optional[str]
    origin_block: Optional[str]
    origin_span: Optional[List[int]]
    text: Optional[str]
    labels: Optional[List[OneAiOutputLabel]]


class OneAiResponse(TypedDict):
    input_text: str
    status: str
    error: str
    output: List[OneAiOutputBlock]

    def to_tags(self) -> List[Tag.CreateRequest]:
        tags: List[Tag.CreateRequest] = []
        if self.output and self.output[0]:
            for label in self.output[0]["labels"]:
                tags.append(label.to_steamship_tag())
        return tags


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
            ret = cast(OneAiResponse, response_dict)
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
