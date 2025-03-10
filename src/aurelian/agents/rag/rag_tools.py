"""
Tools for the RAG agent for retrieval-augmented generation.
"""
import asyncio
from typing import Dict, List

from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search, retrieve_web_page as fetch_web_page
from .rag_config import RagDependencies


async def search_documents(
    ctx: RunContext[RagDependencies], 
    query: str
) -> List[Dict]:
    """
    Performs a retrieval search over the RAG database.
    
    Args:
        ctx: The run context
        query: The search query (any text, such as name of a disease, phenotype, gene, etc.)
        
    Returns:
        A list of document objects matching the query with relevancy scores
    """
    try:
        print(f"SEARCH: {query}")
        
        # Execute the potentially blocking operation in a thread pool
        def _search():
            qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
            objs = []
            for score, row in qr.ranked_rows:
                row["content"] = row["content"][:ctx.deps.max_content_len]
                obj = flatten(row)
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
        raise ModelRetry(f"Error searching documents: {str(e)}")


async def inspect_document(
    ctx: RunContext[RagDependencies], 
    query: str
) -> List[Dict]:
    """
    Returns the content of a document.
    
    Args:
        ctx: The run context
        query: Identifying information for the document (e.g., title)
        
    Returns:
        The document content
    """
    try:
        print(f"INSPECT DOCUMENT: {query}")
        
        # Execute the potentially blocking operation in a thread pool
        def _inspect():
            qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
            for score, row in qr.ranked_rows:
                return row["content"]
            return None
            
        content = await asyncio.to_thread(_inspect)
        
        if not content:
            raise ModelRetry(f"No document found matching: {query}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error inspecting document: {str(e)}")


async def lookup_pmid(
    ctx: RunContext[RagDependencies], 
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
    ctx: RunContext[RagDependencies], 
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
    ctx: RunContext[RagDependencies], 
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