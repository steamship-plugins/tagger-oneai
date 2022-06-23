"""Convenience class to interact with OneAI."""
from json import JSONDecodeError
from typing import Any, Dict, List, Union

import requests
from steamship import SteamshipError

from oneai.api_spec import OneAIInputType, OneAIRequest, OneAIResponse

OneAIConversation = List[Dict[str, str]]


class OneAIClient:
    """Convenience class to interact with OneAI."""

    API_URL = "https://api.oneai.com/api/v0/pipeline"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def request(
        self,
        input: Union[str, OneAIConversation],
        input_type: OneAIInputType,
        steps: List[Dict[str, Any]],
    ) -> OneAIResponse:
        """Perform a OneAI request. Throw a SteamshipError in the event of an error or an empty response.

        See: https://www.oneai.com/docs
        """
        request = OneAIRequest(
            input=input,
            input_type=input_type,
            content_type="application/json" if isinstance(input, list) else "text/plain",
            steps=steps,
        )

        headers = {
            "api-key": self.api_key,
            "content-Type": "application/json",
        }

        response = requests.post(
            url=self.API_URL,
            headers=headers,
            json=request.dict(),
        )

        if not response.ok:
            raise SteamshipError(
                message=f"Request to OneAI failed. Code={response.status_code}. Body={response.text}"
            )

        try:
            response_dict = response.json()
        except JSONDecodeError as e:
            raise SteamshipError(
                message=f"Request from OneAI could not be interpreted as JSON. {e}"
            )

        try:
            return OneAIResponse(**response_dict)
        except Exception as ex:
            raise SteamshipError(
                message=f"Request from OneAI could not be interpreted as a OneAIResponse object. Exception: {ex}",
                error=ex,
            )
