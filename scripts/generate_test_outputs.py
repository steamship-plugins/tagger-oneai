"""Generate testing outputs for various skills."""
import json
import logging
import os
import pathlib
import sys

from src.api import OneAITaggerPluginConfig
from src.oneai.oneai import OneAIClient, OneAIInputType, OneAIRequest

SKILLS = [
    "entities",
    "sentiments",
    "emotions",
    "highlights",
    "keywords",
    "sentences",
    "action-items",
    "article-topics",
    "names",
    "numbers",
    "business-entities",
]


if __name__ == "__main__":
    api_key = os.environ.get("ONEAI_KEY")
    if api_key is None:
        print("Please supply the ONEAI_KEY env variable.")
        sys.exit(1)

    client = OneAIClient(key=api_key)

    logging.basicConfig(level=logging.INFO)
    input_files = pathlib.Path(__file__).parent.parent.absolute() / "test_data" / "inputs"
    output_files = pathlib.Path(__file__).parent.parent.absolute() / "test_data" / "outputs"

    for file in os.listdir(input_files):
        with open(input_files / file, "r") as f:
            text = f.read()
            for skill in SKILLS:
                config = OneAITaggerPluginConfig(
                    api_key=api_key, skills=skill, input_type=OneAIInputType.ARTICLE
                )
                request = OneAIRequest(
                    text=text, input_type=config.input_type, steps=config.steps()
                )
                response = client.request(request)

                output_folder = output_files / skill
                output_folder.mkdir(parents=True, exist_ok=True)

                with open(output_folder / file, "w") as f2:
                    f2.write(json.dumps(response))
