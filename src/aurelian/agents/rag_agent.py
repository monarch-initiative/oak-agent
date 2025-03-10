"""
Agent for retrieval-augmented generation against document collections.

This module re-exports components from the rag/ package for backward compatibility.
"""
from typing import Dict, List

# Re-export from rag package
from aurelian.agents.rag import (
    rag_agent,
    RagDependencies,
    get_config,
    search_documents,
    inspect_document,
    lookup_pmid,
    search_web,
    retrieve_web_page,
    chat,
)

# Re-export the older synchronous versions of functions for compatibility
@rag_agent.tool
def search_documents_sync(ctx, query: str) -> List[Dict]:
    """Legacy synchronous version of search_documents"""
    import asyncio
    return asyncio.run(search_documents(ctx, query))


@rag_agent.tool
def inspect_document_sync(ctx, query: str) -> str:
    """Legacy synchronous version of inspect_document"""
    import asyncio
    return asyncio.run(inspect_document(ctx, query))


@rag_agent.tool
def lookup_pmid_sync(ctx, pmid: str) -> str:
    """Legacy synchronous version of lookup_pmid"""
    import asyncio
    return asyncio.run(lookup_pmid(ctx, pmid))


@rag_agent.tool
def search_web_sync(ctx, query: str) -> str:
    """Legacy synchronous version of search_web"""
    import asyncio
    return asyncio.run(search_web(ctx, query))


@rag_agent.tool
def retrieve_web_page_sync(ctx, url: str) -> str:
    """Legacy synchronous version of retrieve_web_page"""
    import asyncio
    return asyncio.run(retrieve_web_page(ctx, url))