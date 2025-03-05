import asyncio
import gradio as gr
import requests
import tempfile
from pdfminer.high_level import extract_text
from pydantic_ai import Agent, RunContext
from aurelian.utils.search_utils import retrieve_web_page


def get_full_schema(
        url="https://raw.githubusercontent.com/monarch-initiative/ontogpt/main/src/ontogpt/templates/data_sheets_schema.yaml"
    ) -> str:
    """
    Load the full datasheets for datasets schema from GitHub.
    We use the raw URL so that we get plain text.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error: Unable to load full schema."


FULL_SCHEMA = get_full_schema()

# Create the agent using the full schema in the system prompt.
data_sheets_agent = Agent(
    model="openai:gpt-4o",
    system_prompt=f"""
Below is the complete datasheets for datasets schema:

{FULL_SCHEMA}

When provided with a URL to a webpage or PDF describing a dataset, your task is to fetch the 
content, extract all the relevant metadata, and output a YAML document that exactly 
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


def extract_text_from_pdf(pdf_url: str) -> str:
    """
    Download and extract text from a PDF given its URL, using a temporary file.
    """
    response = requests.get(pdf_url)
    if response.status_code != 200:
        return "Error: Unable to retrieve PDF."

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf.flush()  # Ensure all data is written before reading

            text = extract_text(temp_pdf.name)
            return text.strip() if text else "Error: No text extracted from PDF."

    except Exception as e:
        return f"Error extracting PDF text: {e}"


def process_website_or_pdf(url: str) -> str:
    """
    Determine if the URL is a PDF or webpage, retrieve the content, and generate YAML metadata.
    """
    if url.lower().endswith(".pdf"):
        page_content = extract_text_from_pdf(url)
    else:
        # Check the content type in case the file doesn't have a .pdf extension
        response = requests.head(url)
        content_type = response.headers.get("Content-Type", "").lower()

        if "pdf" in content_type:
            page_content = extract_text_from_pdf(url)
        else:
            page_content = retrieve_web_page(url)

    if "Error" in page_content:
        return page_content  # Return error message if retrieval failed

    prompt = f"""
The following is the content of a document describing a dataset:

{page_content}

Using the complete datasheets for datasets schema provided above, extract all the metadata from the document and generate a YAML document that exactly conforms to that schema. Ensure that all required fields are present and the output is valid YAML. The dataset URL is: {url}

Generate only the YAML document.
"""
    result = safe_run(prompt)
    return result.data


def chat(**kwargs):
    """
    Return a Gradio ChatInterface that accepts a URL (webpage or PDF) and outputs the YAML metadata.
    """

    def get_info(url: str, history: list) -> str:
        return process_website_or_pdf(url)

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Datasheets for datasets agent",
        description="Enter a URL to a webpage or PDF describing a dataset. The agent will generate metadata in YAML format according to the complete datasheets for datasets schema.",
        examples=[
            "https://fairhub.io/datasets/2",
            "https://data.chhs.ca.gov/dataset/99bc1fea-c55c-4377-bad8-f00832fd195d/resource/5a6d5fe9-36e6-4aca-ba4c-bf6edc682cf5/download/hci_crime_752-narrative_examples-10-30-15-ada.pdf"
        ]
    )
