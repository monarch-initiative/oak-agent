"""
Agent for extracting dataset metadata following the datasheets for datasets schema.
"""
from pydantic_ai import Agent, RunContext

from .d4d_config import D4DConfig
from .d4d_tools import get_full_schema, process_website_or_pdf


# Create the agent, the full schema will be loaded when needed
data_sheets_agent = Agent(
    model="openai:gpt-4o",
    deps_type=D4DConfig,
    system_prompt="""
Below is the complete datasheets for datasets schema:

{schema}

When provided with a URL to a webpage or PDF describing a dataset, your task is to fetch the 
content, extract all the relevant metadata, and output a YAML document that exactly 
conforms to the above schema. The output must be valid YAML with all required fields 
filled in, following the schema exactly.
""",
)


@data_sheets_agent.system_prompt
async def add_schema(ctx: RunContext[D4DConfig]) -> str:
    """
    Add the full schema to the system prompt.
    
    Args:
        ctx: The run context
        
    Returns:
        The schema to be inserted into the system prompt
    """
    schema = await get_full_schema(ctx)
    return schema


@data_sheets_agent.tool
async def extract_metadata(ctx: RunContext[D4DConfig], url: str) -> str:
    """
    Extract metadata from a dataset description document or webpage.
    
    Args:
        ctx: The run context
        url: The URL of the dataset description (webpage or PDF)
        
    Returns:
        YAML formatted metadata following the datasheets for datasets schema
    """
    # Retrieve the content
    content = await process_website_or_pdf(ctx, url)
    
    # Prepare a prompt to extract metadata
    prompt = f"""
The following is the content of a document describing a dataset:

{content}

Using the complete datasheets for datasets schema provided above, extract all the metadata 
from the document and generate a YAML document that exactly conforms to that schema. 
Ensure that all required fields are present and the output is valid YAML. 
The dataset URL is: {url}

Generate only the YAML document.
"""
    
    # The prompt will be used as the user message
    return prompt