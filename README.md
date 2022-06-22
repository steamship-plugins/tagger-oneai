# OneAI Tagger Plugin - Steamship

This project contains a Steamship Tagger plugin that enables use of OneAI's text tagging pipeline.

## Configuration

This plugin must be configured with the following fields:

* `api_key`    - Your One AI API key
* `input_type` - Either `conversation` or `article`. [One AI Documentation](https://studio.oneai.com/docs?api=Pipeline+API&item=Expected+Input+Format&accordion=Introduction%2CPipeline+API%2CNode.js+SDK+Reference%2CClustering+API)
* `skills`     - A CSV list of One AI "skills" that produce tags

Example skills are:

* `entities` - Tags real-world objects, such as people, organizations, and time frames.
* `topics` - Tags text with relevant topics.
* `sentiment` - Tags text with phrases containing positive and negative sentiment: Output tags: `[POS, NEG]`
* `emotions` - Tags text with phrases describing emotion: Output tags: `[happiness, sadness, anger, surprise, fear]`
* `highlights` - Tags text with selected highlights: Output tags: `[highlight]`
* `keywords` - Tags text with selected keywords.
* `sentences` - Splits sentences by text.
* `action-items` - Tags text for action items.
* `article-topics` - Topics from an article
* `business-entities` - Business Entity labeling
* `names` - Names mentioned
* `numbers` - Numbers mentioned

## Usage

```python
from steamship import File, Plugin, PluginInstance, Steamship

TAGGER_HANDLE = "oneai-tagger"
config = {
    "api_key": "FILL_IN",
    "input_type": "FILL_IN",
    "skills": "FILL_IN"
}

client = Steamship()
plugin = Plugin.get(client, TAGGER_HANDLE).data
plugin_instance = PluginInstance.create(
    client,
    plugin_id=plugin.id,
    plugin_handle=TAGGER_HANDLE,
    upsert=False,
    config=config,
).data
```

## Full Example

Full examples are located as Jupyter notebooks in [examples/](examples/)

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
