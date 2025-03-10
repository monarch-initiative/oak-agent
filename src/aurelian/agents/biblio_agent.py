"""
Agent for working with bibliographies

This module re-exports components from the biblio/ package for backward compatibility.
"""
from typing import Dict, List

# Re-export from biblio package
from aurelian.agents.biblio import (
    biblio_agent,
    BiblioDependencies,
    get_config,
    search_bibliography,
    lookup_pmid,
    search_web,
    retrieve_web_page,
    chat,
)

# Re-export the older synchronous versions of functions for compatibility
@biblio_agent.tool
def search_bibliography_sync(ctx, query: str) -> List[Dict]:
    """Legacy synchronous version of search_bibliography"""
    import asyncio
    return asyncio.run(search_bibliography(ctx, query))


@biblio_agent.tool
def lookup_pmid_sync(ctx, pmid: str) -> str:
    """Legacy synchronous version of lookup_pmid"""
    import asyncio
    return asyncio.run(lookup_pmid(ctx, pmid))


@biblio_agent.tool
def search_web_sync(ctx, query: str) -> str:
    """Legacy synchronous version of search_web"""
    import asyncio
    return asyncio.run(search_web(ctx, query))


@biblio_agent.tool
def retrieve_web_page_sync(ctx, url: str) -> str:
    """Legacy synchronous version of retrieve_web_page"""
    import asyncio
    return asyncio.run(retrieve_web_page(ctx, url))