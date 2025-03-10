"""
Agent for extracting dataset metadata following the datasheets for datasets schema.

This module re-exports components from the d4d/ package for backward compatibility.
"""
import asyncio

# Re-export from d4d package
from aurelian.agents.d4d import (
    data_sheets_agent,
    D4DConfig,
    get_config,
    get_full_schema,
    process_website_or_pdf,
    extract_text_from_pdf,
    chat,
)

# Provide the original synchronous functions for backward compatibility
def get_full_schema_sync(url=None):
    """Legacy synchronous version of get_full_schema"""
    config = get_config()
    ctx = data_sheets_agent._get_run_context(deps=config)
    return asyncio.run(get_full_schema(ctx, url))


FULL_SCHEMA = get_full_schema_sync()


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


def process_website_or_pdf_sync(url: str) -> str:
    """
    Legacy synchronous version of process_website_or_pdf
    """
    config = get_config()
    ctx = data_sheets_agent._get_run_context(deps=config)
    
    # Get the content
    page_content = asyncio.run(process_website_or_pdf(ctx, url))
    
    # Format the prompt
    prompt = f"""
The following is the content of a document describing a dataset:

{page_content}

Using the complete datasheets for datasets schema provided above, extract all the metadata from the document and generate a YAML document that exactly conforms to that schema. Ensure that all required fields are present and the output is valid YAML. The dataset URL is: {url}

Generate only the YAML document.
"""
    # Run the agent with the prompt
    result = safe_run(prompt)
    return result.data