import asyncio
import gradio as gr
from pydantic_ai import Agent, RunContext
from aurelian.utils.search_utils import retrieve_web_page

# Create the agent with your system prompt.
data_sheets_agent = Agent(
    model="openai:gpt-4o",
    system_prompt="""
You are an expert data modeler. When given the content of a webpage that describes a dataset, your task is to extract its metadata and output a YAML document that exactly follows this template:

---
id: <dataset URL>
name: <dataset name>
title: <dataset title>
description: |-
  <detailed description extracted from the webpage>
license: MIT
see_also:
  - <related URL>

prefixes:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  biolink: https://w3id.org/biolink/
  csvw: http://www.w3.org/ns/csvw#
  data_sheets_schema: https://w3id.org/bridge2ai/data-sheets-schema/
  datasets: https://w3id.org/linkml/report
  dcat: http://www.w3.org/ns/dcat#
  example: https://example.org/
  formats: http://www.w3.org/ns/formats/
  frictionless: https://specs.frictionlessdata.io/
  linkml: https://w3id.org/linkml/
  mediatypes: https://www.iana.org/assignments/media-types/
  pav: http://purl.org/pav/
  schema: http://schema.org/
  sh: https://w3id.org/shacl/
  skos: http://www.w3.org/2004/02/skos/core#
  void: http://rdfs.org/ns/void#
default_prefix: data_sheets_schema
default_range: string

imports:
  - linkml:types

When provided with a URL, fetch the webpage, extract the metadata, and output only the YAML document.
""",
)


def safe_run(prompt: str):
    """
    Ensure an event loop is available, then call data_sheets_agent.run_sync.
    """
    try:
        # Try to get the current event loop.
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # If there is no current loop, create one and set it.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # Now call run_sync; since we're inside a worker thread,
    # our agent's run_sync should find the loop we just set.
    return data_sheets_agent.run_sync(prompt)


def process_website(url: str) -> str:
    # Retrieve the webpage content.
    page_content = retrieve_web_page(url)

    # Construct a prompt that embeds the page content.
    prompt = f"""
The following is the content of a webpage describing a dataset:

{page_content}

Using the template below, extract the metadata and generate a YAML document. Fill in the placeholders with information from the webpage.

---
id: {url}
name: <dataset name>
title: <dataset title>
description: |-
  <detailed description extracted from the webpage>
license: MIT
see_also:
  - <related URL>

prefixes:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  biolink: https://w3id.org/biolink/
  csvw: http://www.w3.org/ns/csvw#
  data_sheets_schema: https://w3id.org/bridge2ai/data-sheets-schema/
  datasets: https://w3id.org/linkml/report
  dcat: http://www.w3.org/ns/dcat#
  example: https://example.org/
  formats: http://www.w3.org/ns/formats/
  frictionless: https://specs.frictionlessdata.io/
  linkml: https://w3id.org/linkml/
  mediatypes: https://www.iana.org/assignments/media-types/
  pav: http://purl.org/pav/
  schema: http://schema.org/
  sh: https://w3id.org/shacl/
  skos: http://www.w3.org/2004/02/skos/core#
  void: http://rdfs.org/ns/void#
default_prefix: data_sheets_schema
default_range: string

imports:
  - linkml:types

Generate only the YAML document.
"""
    result = safe_run(prompt)
    return result.data


def chat(**kwargs):
    """
    Return a Gradio ChatInterface that accepts a URL and outputs the YAML metadata.
    """

    def get_info(url: str, history: list) -> str:
        return process_website(url)

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Datasheets4datasets Metadata Agent",
        description="Enter a URL to a webpage describing a dataset. The agent will generate metadata in YAML format.",
        examples=[
            "https://www.kaggle.com/datasets/asinow/car-price-dataset"
        ],
    )
