"""Collection of object specifications used to communicate with the OneAI API."""
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from steamship.data.tags.tag import Tag


class OneAIInputType(str, Enum):
    """Input types supported by OneAI."""

    ARTICLE = "article"
    CONVERSATION = "conversation"
    AUTO = "auto-detect"


class OneAIRequest(BaseModel):
    """OneAI request."""

    input: Union[str, List[Dict[str, str]]]
    input_type: OneAIInputType
    steps: List[Dict[str, str]]
    content_type: str = "text/plain"


class OneAISkill(str, Enum):
    """Skills supported by OneAI."""

    EMOTIONS = "emotions"
    ENTITIES = "entities"
    ANONYMIZE = "anonymize"
    ACTION_ITEMS = "action-items"
    DIALOGUE_SEGMENTATION = "dialogue-segmentation"
    KEYWORDS = "keywords"
    HIGHLIGHTS = "highlights"
    SENTIMENTS = "sentiments"
    NAMES = "names"
    NUMBERS = "numbers"
    PRICING = "business-entities"
    SUMMARIZE = "summarize"
    TOPICS = "topics"


class OneAIOutputLabel(BaseModel):
    """Output label listed inside a OneAI Response."""

    type: Optional[str]
    name: Optional[str]
    skill: Optional[str]
    span: Optional[List[int]]
    span_text: Optional[str]
    data: Optional[dict]

    def to_steamship_tag(self) -> Tag.CreateRequest:
        """Convert to a Steamship Tag."""
        return Tag.CreateRequest(
            kind=self.skill,
            name=self.name or self.type,
            start_idx=self.span[0] if len(self.span) == 2 else None,
            end_idx=self.span[1] if len(self.span) == 2 else None,
            value=self.data,
        )


class OneAIOutputBlock(BaseModel):
    """A output block inside OneAI's response."""

    block_id: Optional[str]
    generating_step: Optional[str]
    origin_block: Optional[str]
    origin_span: Optional[List[int]]
    text: Optional[str]
    labels: Optional[List[OneAIOutputLabel]]


class OneAIResponse(BaseModel):
    """OneAI's response."""

    input_text: str
    status: str
    error: Optional[str] = None
    output: Optional[List[OneAIOutputBlock]] = None

    def to_steamship_tags(self) -> List[Tag.CreateRequest]:
        """Convert to a list of Steamship Tags."""
        return [label.to_steamship_tag() for output in self.output or [] for label in output.labels]
