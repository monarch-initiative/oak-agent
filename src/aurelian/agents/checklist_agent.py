"""
Agent for validating papers against checklists, e.g STREAMS

This module re-exports components from the checklist/ package for backward compatibility.
"""
from typing import Dict, List

# Re-export from checklist package
from aurelian.agents.checklist import (
    checklist_agent,
    add_checklists,
    ChecklistDependencies,
    get_config,
    all_checklists,
    retrieve_text_from_pmid,
    retrieve_text_from_doi,
    fetch_checklist,
    chat,
)

# Re-export the older synchronous versions of functions for compatibility
@checklist_agent.tool
def retrieve_text_from_pmid_sync(ctx, pmid: str) -> str:
    """Legacy synchronous version of retrieve_text_from_pmid"""
    import asyncio
    return asyncio.run(retrieve_text_from_pmid(ctx, pmid))


@checklist_agent.tool
def retrieve_text_from_doi_sync(ctx, doi: str) -> str:
    """Legacy synchronous version of retrieve_text_from_doi"""
    import asyncio
    return asyncio.run(retrieve_text_from_doi(ctx, doi))


@checklist_agent.tool
def fetch_checklist_sync(ctx, checklist_id: str) -> str:
    """Legacy synchronous version of fetch_checklist"""
    import asyncio
    return asyncio.run(fetch_checklist(ctx, checklist_id))