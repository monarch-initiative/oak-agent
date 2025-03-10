"""
Tools for the Biblio agent for working with bibliographic data.
"""
import asyncio
from typing import Dict, List

from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search, retrieve_web_page as fetch_web_page
from .biblio_config import BiblioDependencies


async def search_bibliography(
    ctx: RunContext[BiblioDependencies], 
    query: str
) -> List[Dict]:
    """
    Performs a retrieval search over the biblio database.

    Args:
        ctx: The run context
        query: The search query (disease, phenotype, gene, etc.)

    Returns:
        A list of biblio objects matching the query

    The query can be any text, such as name of a disease, phenotype, gene, etc.

    The objects returned are "biblio" which is a structured representation
    of a patient. Each is uniquely identified by a phenopacket ID (essentially
    the patient ID).

    The objects returned are summaries of biblio; omit some details such
    as phenotypes. Use `lookup_biblio` to retrieve full details of a phenopacket.

    Note that the phenopacket store may not be complete, and the retrieval
    method may be imperfect
    """
    try:
        print(f"SEARCH: {query}")
        
        # Execute the potentially blocking operation in a thread pool
        def _search():
            qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
            objs = []
            for score, row in qr.ranked_rows:
                obj = flatten(row, preserve_keys=["interpretations", "diseases"])
                obj["relevancy_score"] = score
                objs.append(obj)
                print(f"RESULT: {obj}")
            return objs
            
        objs = await asyncio.to_thread(_search)
        
        if not objs:
            raise ModelRetry(f"No results found for query: {query}")
            
        return objs
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching bibliography: {str(e)}")


async def lookup_pmid(
    ctx: RunContext[BiblioDependencies], 
    pmid: str
) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Args:
        ctx: The run context
        pmid: The PubMed ID to look up (format: "PMID:nnnnnnn")

    Returns:
        The full text if available, otherwise abstract

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).

    NOTE: Phenopacket IDs are typically of the form PMID_nnn_PatientNumber,
    but this should be be assumed. To reliably get PMIDs for a phenopacket,
    use `lookup_phenopacket` to retrieve examine the `externalReferences`
    field.
    """
    try:
        print(f"LOOKUP PMID: {pmid}")
        
        # Execute the potentially blocking operation in a thread pool
        text = await asyncio.to_thread(get_pmid_text, pmid)
        
        if not text or text.strip() == "":
            raise ModelRetry(f"No text found for PMID: {pmid}")
            
        return text
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving text from PMID: {str(e)}")


async def search_web(
    ctx: RunContext[BiblioDependencies], 
    query: str
) -> str:
    """
    Search the web using a text query.

    Args:
        ctx: The run context
        query: The search query

    Returns:
        Matching web pages plus summaries

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.
    """
    try:
        print(f"Web Search: {query}")
        
        # Execute the potentially blocking operation in a thread pool
        results = await asyncio.to_thread(web_search, query)
        
        if not results or results.strip() == "":
            raise ModelRetry(f"No web search results found for query: {query}")
            
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching web: {str(e)}")


async def retrieve_web_page(
    ctx: RunContext[BiblioDependencies], 
    url: str
) -> str:
    """
    Fetch the contents of a web page.

    Args:
        ctx: The run context
        url: The URL to fetch

    Returns:
        The contents of the web page
    """
    try:
        print(f"Fetch URL: {url}")
        
        # Execute the potentially blocking operation in a thread pool
        content = await asyncio.to_thread(fetch_web_page, url)
        
        if not content or content.strip() == "":
            raise ModelRetry(f"No content found for URL: {url}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving web page: {str(e)}")