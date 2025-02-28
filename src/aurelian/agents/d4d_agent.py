import asyncio
import gradio as gr
import requests
from pydantic_ai import Agent, RunContext
from aurelian.utils.search_utils import retrieve_web_page


def get_full_schema(
        url="https://raw.githubusercontent.com/monarch-initiative/ontogpt/main/src/ontogpt/templates/data_sheets_schema.yaml"
    ) -> str:
    """
    Load the full datasheets for datasets schema from GitHub.
    We use the raw URL so that we get plain text.
    """
    url = url
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error: Unable to load full schema."


FULL_SCHEMA = get_full_schema()

# Create the agent using the full schema in the system prompt.
data_sheets_agent = Agent(
    model="openai:o1",
    system_prompt=f"""
Below is the complete datasheets for datasets schema:

{FULL_SCHEMA}

When provided with a URL to a webpage describing a dataset, your task is to fetch the 
webpage, extract all the relevant metadata, and output a YAML document that exactly 
conforms to the above schema. The output must be valid YAML with all required fields 
filled in, following the schema exactly.
""",
)


def safe_run(prompt: str):
    """
    Ensure an event loop is available and then call the agent's synchronous method.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return data_sheets_agent.run_sync(prompt)


def process_website(url: str) -> str:
    """
    Retrieve the webpage content from the given URL, construct a prompt that
    instructs the agent to extract metadata following the full schema, and return the YAML output.
    """
    page_content = retrieve_web_page(url)

    prompt = f"""
The following is the content of a webpage describing a dataset:

{page_content}

Using the complete datasheets for datasets schema provided above, extract all the metadata from the webpage and generate a YAML document that exactly conforms to that schema. Ensure that all required fields are present and the output is valid YAML. The dataset URL is: {url}

Generate only the YAML document.
"""
    result = safe_run(prompt)
    return result.data


def chat(**kwargs):
    """
    Return a Gradio ChatInterface that accepts a URL and outputs the YAML metadata.
    An example URL is provided.
    """

    def get_info(url: str, history: list) -> str:
        return process_website(url)

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Datasheets for datasets agent",
        description="Enter a URL to a webpage describing a dataset. The agent will generate metadata in YAML format according to the complete datasheets for datasets schema.",
        examples=["https://www.kaggle.com/datasets/asinow/car-price-dataset"]
    )
