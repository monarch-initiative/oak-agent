"""
Agent for validating papers against checklists, e.g STREAMS
"""
from dataclasses import dataclass
from typing import Dict, List

import yaml
from pydantic_ai import Agent, RunContext

from aurelian.agents.checklist import CONTENT_DIR, CONTENT_METADATA_PATH
from aurelian.utils.async_utils import run_sync
from aurelian.utils.pubmed_utils import get_doi_text, get_pmid_text


def all_checklists() -> Dict:
    with open(CONTENT_METADATA_PATH) as f:
        return yaml.safe_load(f)


@dataclass
class ChecklistDependencies:
    pass


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
    meta = all_checklists()
    return "\n".join([f"- {c['id']}: {c['title']}" for c in meta["checklists"]])


@checklist_agent.tool
def retrieve_text_from_pmid(ctx: RunContext[ChecklistDependencies], pmid: str) -> str:
    """Lookup the text of a PubMed ID, using its PMID.

    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    return get_pmid_text(pmid)


@checklist_agent.tool
def retrieve_text_from_doi(ctx: RunContext[ChecklistDependencies], doi: str) -> str:
    """Lookup the text of a DOI

    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP DOI: {doi}")
    return get_doi_text(doi)


@checklist_agent.tool
def fetch_checklist(ctx: RunContext[ChecklistDependencies], checklist_id: str) -> str:
    """Lookup the checklist entry for a given checklist accession number

    Args:
        checklist_id: E.g. STREAM, STORMS, ARRIVE

    """
    meta = all_checklists()
    selected_checklist = None
    checklist_id = checklist_id.lower()
    for checklist in meta["checklists"]:
        if checklist["id"] == checklist_id:
            selected_checklist = checklist
            break
        if checklist["title"] == checklist_id:
            selected_checklist = checklist
            break
    if not selected_checklist:
        return f"Could not find checklist with ID {checklist_id}"
    id = selected_checklist["id"]
    path = CONTENT_DIR / f"{id}.csv"
    if not path.exists():
        raise AssertionError(f"Checklist file not found: {path}")
    with open(path) as f:
        return f.read()


def chat(**kwargs):
    import gradio as gr

    deps = ChecklistDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: checklist_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="Checklist AI Assistant",
        examples=[
            ["Evaluate https://journals.asm.org/doi/10.1128/mra.01361-19 using STREAMS"],
            [
                (
                    "Check the paper 'Exploration of the Biosynthetic Potential of the Populus Microbiome'"
                    " https://journals.asm.org/doi/10.1128/msystems.00045-18"
                )
            ],
        ],
    )
