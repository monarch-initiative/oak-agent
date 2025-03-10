"""
Tools for the Ontology Mapper agent.
"""
import asyncio
from functools import lru_cache
from typing import Dict, List, Optional

from oaklib import get_adapter
from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.search_utils import web_search, retrieve_web_page as fetch_web_page
from .ontology_mapper_config import OntologyMapperDependencies, get_config


@lru_cache
def get_ontology_adapter(ont: str):
    """
    Get an adapter for the specified ontology.

    Args:
        ont: The ontology ID to get an adapter for (e.g. cl, go, uberon)

    Returns:
        An OAK adapter for the specified ontology
    """
    ont = ont.lower()
    return get_adapter(f"sqlite:obo:{ont}")


async def search_terms(
    ctx: RunContext[OntologyMapperDependencies], 
    ontology_id: str, 
    query: str
) -> List[Dict]:
    """
    Finds similar ontology terms to the search query.

    For example:

        ```
        search_terms("go", "cycle cycle and related processes")
        ```

    Relevancy ranking is used, with semantic similarity, which means
    queries need only be close in semantic space. E.g. while GO does not
    deal with diseases, this may return relevant pathways or structures:

        ```
        search_terms("go", "terms most relevant to Parkinson disease")
        ```

    Args:
        ctx: The run context
        ontology_id: The ontology ID to search in (e.g. cl, go, uberon)
        query: The search query
        
    Returns:
        A list of matching ontology terms
    """
    print(f"Term Search: {ontology_id} {query}")
    
    try:
        if " " in ontology_id:
            raise ModelRetry(
                "Invalid ontology ID, use an OBO style ID like cl, mondo, chebi, etc."
            )
            
        config = ctx.deps or get_config()
        if ontology_id.lower() not in [ont.lower() for ont in config.ontologies]:
            allowed_onts = ", ".join(config.ontologies)
            raise ModelRetry(
                f"Ontology '{ontology_id}' not in allowed list: {allowed_onts}"
            )
            
        adapter = get_ontology_adapter(ontology_id)
        # Execute the potentially blocking operation in a thread pool
        results = await asyncio.to_thread(
            search_ontology, 
            adapter, 
            query, 
            limit=config.max_search_results
        )
        
        if not results:
            raise ModelRetry(f"No results found for query '{query}' in ontology '{ontology_id}'")
            
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching ontology: {str(e)}")


async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Args:
        query: The search query
        
    Returns: 
        Matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    
    try:
        # Execute the potentially blocking operation in a thread pool
        results = await asyncio.to_thread(web_search, query)
        
        if not results or results.strip() == "":
            raise ModelRetry(f"No web search results found for query: {query}")
            
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error searching the web: {str(e)}")


async def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Args:
        url: The URL of the web page to retrieve
        
    Returns:
        The contents of the web page
    """
    print(f"Fetch URL: {url}")
    
    try:
        # Execute the potentially blocking operation in a thread pool
        content = await asyncio.to_thread(fetch_web_page, url)
        
        if not content or content.strip() == "":
            raise ModelRetry(f"No content found at URL: {url}")
            
        return content
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error retrieving web page: {str(e)}")