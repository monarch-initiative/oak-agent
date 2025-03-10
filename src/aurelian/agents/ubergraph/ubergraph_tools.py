"""
Tools for interacting with the UberGraph SPARQL endpoint.
"""
import asyncio
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_ai import RunContext, ModelRetry
from SPARQLWrapper import JSON, SPARQLWrapper

from .ubergraph_config import Dependencies, get_config


class QueryResults(BaseModel):
    """Results of a SPARQL query."""
    results: List[Dict] = []


def simplify_value(v: Dict, prefixes=None) -> Any:
    """
    Simplify a SPARQL query result value.
    
    Args:
        v: The value to simplify
        prefixes: Optional mapping of prefixes to expansions
        
    Returns:
        The simplified value
    """
    if prefixes and v["type"] == "uri":
        for prefix, expansion in prefixes.items():
            if v["value"].startswith(expansion):
                return f"{prefix}:{v['value'][len(expansion):]}"
    return v["value"]


def simplify_results(results: Dict, prefixes=None, limit=20) -> List[Dict]:
    """
    Simplify SPARQL query results.
    
    Args:
        results: The query results to simplify
        prefixes: Optional mapping of prefixes to expansions
        limit: Maximum number of results to return
        
    Returns:
        A list of simplified results
    """
    rows = []
    n = 0
    for r in results["results"]["bindings"]:
        n += 1
        if n > limit:
            break
        row = {}
        for k, v in r.items():
            row[k] = simplify_value(v, prefixes)
        rows.append(row)
    return rows


async def query_ubergraph(ctx: RunContext[Dependencies], query: str) -> QueryResults:
    """
    Performs a SPARQL query over Ubergraph then returns the results as triples.

    Ubergraph is a triplestore that contains many OBO ontologies and precomputed
    relation graph edges.
    
    Args:
        ctx: The run context
        query: The SPARQL query to execute
        
    Returns:
        The query results
    """
    config = ctx.deps or get_config()
    prefixes = config.prefixes
    endpoint = config.endpoint
    
    # Add prefixes to query
    prefixed_query = ""
    for k, v in prefixes.items():
        prefixed_query += f"PREFIX {k}: <{v}>\n"
    prefixed_query += query
    
    print("## Query")
    print(prefixed_query)
    print("##")
    
    try:
        # Create SPARQL wrapper
        sw = SPARQLWrapper(endpoint)
        sw.setQuery(prefixed_query)
        sw.setReturnFormat(JSON)
        
        # Execute the query in a thread pool
        ret = await asyncio.to_thread(sw.queryAndConvert)
        
        # Process the results
        results = simplify_results(ret, prefixes, limit=config.max_results)
        print("num results=", len(results))
        print("results=", results)
        
        if not results:
            raise ModelRetry(f"No results found for SPARQL query. Try refining your query.")
            
        return QueryResults(results=results)
    except Exception as e:
        if "ModelRetry" in str(type(e)):
            raise e
        
        # Handle specific SPARQL errors
        if "syntax error" in str(e).lower():
            raise ModelRetry(f"SPARQL syntax error: {str(e)}")
        elif "time" in str(e).lower() and "out" in str(e).lower():
            raise ModelRetry("Query timed out. Try to simplify your query or reduce its scope.")
        else:
            raise ModelRetry(f"Error executing SPARQL query: {str(e)}")