"""
Agent for validating papers against checklists, e.g STREAMS
"""
from pydantic_ai import Agent, RunContext

from .checklist_config import ChecklistDependencies
from .checklist_tools import all_checklists, retrieve_text_from_pmid, retrieve_text_from_doi, fetch_checklist


checklist_agent = Agent(
    model="openai:gpt-4o",
    system_prompt=(
        "Your role is to evaluate papers to ensure they conform to relevant checklists."
        "When asked to look at or review a paper, you should first select the "
        "appropriate checklist from the list of available checklists. Retrieve the checklist."
        " evaluate the paper according to the checklist, and return results that include both"
        " complete evaluation for each checklist item, and a general summary."
        " if a particular checklist item succeeds, say PASS and then any relevant details."
        " Include examples if relevant. If a particular checklist item fails, say FAIL and provide"
        " Explanation. If unclear state OTHER and provide an explanation."
        " Return this as a markdown table."
        "\nThe available checklists are:"
    ),
    deps_type=ChecklistDependencies,
)


@checklist_agent.system_prompt
def add_checklists(ctx: RunContext[ChecklistDependencies]) -> str:
    """
    Add available checklists to the system prompt.
    
    Args:
        ctx: The run context
        
    Returns:
        A string containing the list of available checklists
    """
    meta = all_checklists()
    return "\n".join([f"- {c['id']}: {c['title']}" for c in meta["checklists"]])


@checklist_agent.tool
async def retrieve_text_from_pmid_tool(ctx: RunContext[ChecklistDependencies], pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Args:
        ctx: The run context
        pmid: The PubMed ID to look up
    
    Returns: 
        Full text if available, otherwise abstract
    """
    return await retrieve_text_from_pmid(ctx, pmid)


@checklist_agent.tool
async def retrieve_text_from_doi_tool(ctx: RunContext[ChecklistDependencies], doi: str) -> str:
    """
    Lookup the text of a DOI.

    Args:
        ctx: The run context
        doi: The DOI to look up
    
    Returns: 
        Full text if available, otherwise abstract
    """
    return await retrieve_text_from_doi(ctx, doi)


@checklist_agent.tool
async def fetch_checklist_tool(ctx: RunContext[ChecklistDependencies], checklist_id: str) -> str:
    """
    Lookup the checklist entry for a given checklist accession number.

    Args:
        ctx: The run context
        checklist_id: The checklist ID (e.g. STREAM, STORMS, ARRIVE)
    
    Returns:
        The content of the checklist
    """
    return await fetch_checklist(ctx, checklist_id)