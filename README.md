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
This example uses the `action-items` skill of OneAI via Steamship.

To authenticate with Steamship, install the Steamship CLI with:

```bash
> npm install -g @steamship/cli
```

And then login with:

```bash
> ship login
```

```python
from steamship import Steamship, Plugin, PluginInstance, File, Block, Tag
PLUGIN_HANDLE = 'oneai-tagger'
PLUGIN_CONFIG = {
    "skills": 'action-items',
    "input_type": 'article',
    "api_key": "84ae4e01-e565-4791-a30c-181534f3eef4"
}

steamship = Steamship(profile="staging") # Without arguments, credentials in ~/.steamship.json will be used.
oneai_plugin = Plugin.get(client=steamship, handle=PLUGIN_HANDLE).data # Managed globally by Steamship
oneai_plugin_instance = PluginInstance.create(
    client=steamship,
    plugin_id=oneai_plugin.id,
    config=PLUGIN_CONFIG
).data

file = File.create(
    client=steamship,
    blocks=[Block.CreateRequest(text="YOUR_TEXT", tags=[Tag.CreateRequest(name="Hi")]) ]
).data

tag_results = file.tag(plugin_instance=oneai_plugin_instance.handle)
tag_results.wait()

file = file.refresh().data
for block in file.blocks:
    for tag in file.blocks.tags:
        text = block.text[tag.start_idx or 0:tag.end_idx or -1]
        print(f"[{tag.kind} / {tag.name}]\n{text}")
```

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
