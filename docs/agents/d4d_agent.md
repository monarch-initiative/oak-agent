# D4D Agent (Datasheets for Datasets)

The D4D Agent (Datasheets for Datasets) extracts structured metadata from dataset documentation according to the [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) schema. It can analyze both web pages and PDF documents describing datasets and generate standardized YAML metadata.

## Features

- Extracts metadata from web pages describing datasets
- Processes PDF documentation with text extraction
- Generates structured metadata in YAML format
- Follows the comprehensive Datasheets for Datasets schema
- Auto-detection of document type (web page or PDF)

## Usage

### Python API

```python
from aurelian.agents.d4d import data_sheets_agent, get_config

# Initialize dependencies
deps = get_config()

# Extract metadata from a dataset web page
result = await data_sheets_agent.run(
    "https://fairhub.io/datasets/2",
    deps=deps
)

# Get the YAML metadata
print(result.data)
```

### Command Line Interface

```bash
aurelian datasheets "https://fairhub.io/datasets/2"
```

### Gradio Interface

```python
from aurelian.agents.d4d import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The D4D Agent provides the following tools:

### extract_metadata

Extracts metadata from a dataset description document or webpage, returning YAML formatted metadata following the datasheets schema.

### process_website_or_pdf

Determines if the URL points to a PDF or webpage, and retrieves the appropriate content.

### extract_text_from_pdf

Downloads and extracts text from a PDF given its URL.

### get_full_schema

Loads the full datasheets for datasets schema from GitHub.

## Configuration

The D4D Agent can be configured through:

- Environment variables:
  - `AURELIAN_D4D_SCHEMA_URL`: Custom URL for the schema YAML
  - `AURELIAN_WORKDIR`: Working directory for the agent
  
- Direct configuration:
  - Pass `schema_url` parameter to `get_config()`

## Examples

### Example 1: Extracting metadata from a web page

```
https://fairhub.io/datasets/2
```

### Example 2: Extracting metadata from a PDF document

```
https://data.chhs.ca.gov/dataset/99bc1fea-c55c-4377-bad8-f00832fd195d/resource/5a6d5fe9-36e6-4aca-ba4c-bf6edc682cf5/download/hci_crime_752-narrative_examples-10-30-15-ada.pdf
```