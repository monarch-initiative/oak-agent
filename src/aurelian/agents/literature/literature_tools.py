"""
Tools for the literature agent.
"""
from typing import Optional, List, Dict

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.literature.literature_config import LiteratureDependencies
from aurelian.utils.doi_fetcher import DOIFetcher
from aurelian.utils.pubmed_utils import (
    get_pmid_text,
    get_doi_text,
    pmid_to_doi,
    doi_to_pmid,
    get_abstract_from_pubmed,
)
from aurelian.utils.pdf_fetcher import extract_text_from_pdf
from aurelian.utils.search_utils import web_search, retrieve_web_page


async def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed article by its PMID.
    
    A PMID should be of the form "PMID:nnnnnnn" (no underscores).
    
    Args:
        pmid: The PubMed ID to look up
        
    Returns:
        str: Full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    try:
        result = get_pmid_text(pmid)
        if not result or "Error" in result:
            raise ModelRetry(f"Could not retrieve text for PMID: {pmid}. Try using the abstract only or a different identifier.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error retrieving PMID {pmid}: {str(e)}. Try using the abstract only or a different identifier.")


async def lookup_doi(doi: str) -> str:
    """
    Lookup the text of an article by its DOI.
    
    Args:
        doi: The DOI to look up (e.g., "10.1038/nature12373")
        
    Returns:
        str: Full text if available, otherwise abstract
    """
    print(f"LOOKUP DOI: {doi}")
    try:
        result = get_doi_text(doi)
        if not result or "Error" in result or "not available" in result.lower():
            raise ModelRetry(f"Could not retrieve text for DOI: {doi}. Try using a PubMed ID or a different approach.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error retrieving DOI {doi}: {str(e)}. Try using a PubMed ID or a different approach.")


async def convert_pmid_to_doi(pmid: str) -> Optional[str]:
    """
    Convert a PubMed ID to a DOI.
    
    Args:
        pmid: The PubMed ID to convert
        
    Returns:
        str: The corresponding DOI, or None if not found
    """
    print(f"CONVERT PMID TO DOI: {pmid}")
    try:
        result = pmid_to_doi(pmid)
        if not result:
            raise ModelRetry(f"Could not convert PMID {pmid} to DOI. This article may not have a DOI assigned.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error converting PMID {pmid} to DOI: {str(e)}")


async def convert_doi_to_pmid(doi: str) -> Optional[str]:
    """
    Convert a DOI to a PubMed ID.
    
    Args:
        doi: The DOI to convert
        
    Returns:
        str: The corresponding PubMed ID, or None if not found
    """
    print(f"CONVERT DOI TO PMID: {doi}")
    try:
        result = doi_to_pmid(doi)
        if not result:
            raise ModelRetry(f"Could not convert DOI {doi} to PMID. This article may not be indexed in PubMed.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error converting DOI {doi} to PMID: {str(e)}")


async def get_article_abstract(pmid: str) -> str:
    """
    Get only the abstract of an article by its PubMed ID.
    
    Args:
        pmid: The PubMed ID to look up
        
    Returns:
        str: The article abstract
    """
    print(f"GET ABSTRACT: {pmid}")
    try:
        result = get_abstract_from_pubmed(pmid)
        if not result or result.endswith("No abstract available"):
            raise ModelRetry(f"No abstract available for PMID {pmid}. This article may not have an abstract or the PMID may be incorrect.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error retrieving abstract for PMID {pmid}: {str(e)}")


async def extract_text_from_pdf_url(ctx: RunContext[LiteratureDependencies], pdf_url: str) -> str:
    """
    Extract text from a PDF at the given URL.
    
    Args:
        ctx: The run context
        pdf_url: URL to the PDF file
        
    Returns:
        str: The extracted text content
    """
    print(f"EXTRACT PDF: {pdf_url}")
    try:
        result = extract_text_from_pdf(pdf_url)
        if not result or "Error" in result:
            raise ModelRetry(f"Could not extract text from PDF at {pdf_url}. The URL may be invalid or the PDF may be password-protected.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error extracting text from PDF {pdf_url}: {str(e)}")


async def search_literature_web(query: str) -> str:
    """
    Search the web for scientific literature using a text query.
    
    Args:
        query: The search query (e.g., "alzheimer's disease genetics 2023")
        
    Returns:
        str: Search results with summaries
    """
    print(f"LITERATURE WEB SEARCH: {query}")
    try:
        result = web_search(query)
        if not result:
            raise ModelRetry(f"No search results found for query: {query}. Try using different keywords.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error searching the web for '{query}': {str(e)}")


async def retrieve_literature_page(url: str) -> str:
    """
    Fetch the contents of a literature webpage.
    
    Args:
        url: The URL to fetch
        
    Returns:
        str: The contents of the webpage
    """
    print(f"FETCH LITERATURE URL: {url}")
    try:
        result = retrieve_web_page(url)
        if not result or len(result.strip()) < 20:
            raise ModelRetry(f"Could not retrieve meaningful content from {url}. The URL may be invalid or require authentication.")
        return result
    except Exception as e:
        raise ModelRetry(f"Error retrieving webpage {url}: {str(e)}")