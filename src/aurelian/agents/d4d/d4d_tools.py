"""
Tools for the D4D (Datasheets for Datasets) agent.
"""
import asyncio
import tempfile
from typing import Optional

import requests
from pdfminer.high_level import extract_text
from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.search_utils import retrieve_web_page as fetch_web_page
from .d4d_config import D4DConfig


async def get_full_schema(
    ctx: RunContext[D4DConfig],
    url: Optional[str] = None
) -> str:
    """
    Load the full datasheets for datasets schema from GitHub.
    
    Args:
        ctx: The run context
        url: Optional URL override for the schema location
        
    Returns:
        The schema text content
    """
    try:
        schema_url = url or ctx.deps.schema_url
        
        # Execute the potentially blocking operation in a thread pool
        def _fetch_schema():
            response = requests.get(schema_url)
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to load schema: HTTP {response.status_code}")
                
        schema_text = await asyncio.to_thread(_fetch_schema)
        
        if not schema_text or schema_text.strip() == "":
            raise ModelRetry(f"Empty schema returned from URL: {schema_url}")
            
        return schema_text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error loading schema: {str(e)}")


async def extract_text_from_pdf(
    ctx: RunContext[D4DConfig],
    pdf_url: str
) -> str:
    """
    Download and extract text from a PDF given its URL.
    
    Args:
        ctx: The run context
        pdf_url: The URL of the PDF to extract text from
        
    Returns:
        The extracted text content
    """
    try:
        # Execute the potentially blocking operation in a thread pool
        def _extract_pdf():
            response = requests.get(pdf_url)
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve PDF: HTTP {response.status_code}")
                
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
                temp_pdf.write(response.content)
                temp_pdf.flush()  # Ensure all data is written before reading
                
                text = extract_text(temp_pdf.name)
                if not text or text.strip() == "":
                    raise Exception("No text extracted from PDF")
                    
                return text.strip()
                
        pdf_text = await asyncio.to_thread(_extract_pdf)
        return pdf_text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error extracting PDF text: {str(e)}")


async def retrieve_web_page(
    ctx: RunContext[D4DConfig],
    url: str
) -> str:
    """
    Retrieve the content of a web page.
    
    Args:
        ctx: The run context
        url: The URL of the web page to retrieve
        
    Returns:
        The web page content
    """
    try:
        # Execute the potentially blocking operation in a thread pool
        content = await asyncio.to_thread(fetch_web_page, url)
        
        if not content or content.strip() == "":
            raise ModelRetry(f"No content found for URL: {url}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving web page: {str(e)}")


async def process_website_or_pdf(
    ctx: RunContext[D4DConfig],
    url: str
) -> str:
    """
    Determine if the URL is a PDF or webpage, retrieve the content.
    
    Args:
        ctx: The run context
        url: The URL of the content to process
        
    Returns:
        The extracted content from the PDF or web page
    """
    try:
        # Check if it's a PDF by extension or content type
        is_pdf = False
        
        if url.lower().endswith(".pdf"):
            is_pdf = True
        else:
            # Check the content type in case the file doesn't have a .pdf extension
            def _check_content_type():
                response = requests.head(url)
                content_type = response.headers.get("Content-Type", "").lower()
                return "pdf" in content_type
                
            is_pdf = await asyncio.to_thread(_check_content_type)
        
        # Retrieve the content based on the type
        if is_pdf:
            return await extract_text_from_pdf(ctx, url)
        else:
            return await retrieve_web_page(ctx, url)
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error processing URL: {str(e)}")