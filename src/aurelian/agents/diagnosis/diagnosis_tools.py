"""
Tools for the Diagnosis agent.
"""
import asyncio
from functools import lru_cache
from typing import Dict, List, Optional

from oaklib import get_adapter
from pydantic_ai import RunContext, ModelRetry

from aurelian.utils.data_utils import obj_to_dict
from aurelian.utils.ontology_utils import search_ontology
from aurelian.utils.search_utils import web_search, retrieve_web_page as fetch_web_page
from .diagnosis_config import DiagnosisDependencies, get_config, HAS_PHENOTYPE


@lru_cache
def get_mondo_adapter():
    """
    Get the MONDO ontology adapter.
    
    Returns:
        The MONDO ontology adapter from OAK
    """
    return get_adapter("sqlite:obo:mondo")


async def find_disease_id(
    ctx: RunContext[DiagnosisDependencies], 
    query: str
) -> List[Dict]:
    """
    Finds the disease ID for a given search term.

    OAK search term syntax is used; the default strategy is to match
    labels:

        ```
        find_disease_id("Dravet syndrome")
        ```

    You can use OAK expressions, e.g, all labels
    that start with "Peroxisomal biogenesis disorder":

        ```
        find_disease_id("l^Peroxisomal biogenesis disorder")
        ```

    Args:
        ctx: The run context
        query: The label search term to use
        
    Returns:
        List of matching disease IDs and names
    """
    print(f"Disease Search: {query}")
    
    try:
        config = ctx.deps or get_config()
        adapter = get_mondo_adapter()
        
        # Execute the potentially blocking operation in a thread pool
        results = await asyncio.to_thread(
            search_ontology, 
            adapter, 
            query, 
            limit=config.max_search_results
        )
        
        if not results:
            raise ModelRetry(
                f"No disease IDs found for query: {query}. Try a different search term."
            )
            
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error finding disease ID: {str(e)}")


async def find_disease_phenotypes(
    ctx: RunContext[DiagnosisDependencies], 
    query: str
) -> List[Dict]:
    """
    Finds the phenotypes for a disease ID.

    Example:

        ```
        find_disease_phenotypes("MONDO:0007947")
        ```

    Args:
        ctx: The run context
        query: The disease ID to search for (should be an ID but can be a name)
        
    Returns:
        List of phenotypes for the disease
    """
    print(f"Phenotype query: {query}")
    
    try:
        config = ctx.deps or get_config()
        
        # Determine if we have a disease ID or need to search for one
        if ":" in query:
            query_ids = [query]
        else:
            # Find the disease ID from the name
            disease_results = await find_disease_id(ctx, query)
            if not disease_results:
                raise ModelRetry(f"Could not find disease for query: {query}")
                
            # Extract just the IDs from the results
            query_ids = [result.get("id") for result in disease_results if "id" in result]
            if not query_ids:
                raise ModelRetry(f"Could not find valid disease IDs for query: {query}")
        
        # Get the phenotype associations
        monarch_adapter = config.monarch_adapter
        
        # Execute the potentially blocking operation in a thread pool
        assocs = await asyncio.to_thread(
            monarch_adapter.associations, 
            subjects=query_ids, 
            predicates=[HAS_PHENOTYPE]
        )
        
        # Convert to dictionaries
        results = []
        for assoc in assocs:
            dict_assoc = await asyncio.to_thread(obj_to_dict, assoc)
            results.append(dict_assoc)
        
        if not results:
            disease_label = query
            if query_ids and query_ids[0] != query:
                disease_label = f"{query} ({query_ids[0]})"
            raise ModelRetry(f"No phenotypes found for disease: {disease_label}")
            
        print(f"Results[{query_ids}]: {results}")
        return results
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        raise ModelRetry(f"Error finding disease phenotypes: {str(e)}")


async def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note: This will not retrieve the full content. For that, use `retrieve_web_page`.

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