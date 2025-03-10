"""
Agent for creating ontology mappings.
"""
from pydantic_ai import Agent, RunContext

from .ontology_mapper_config import OntologyMapperDependencies, get_config
from .ontology_mapper_tools import (
    search_terms,
    search_web,
    retrieve_web_page,
)

# System prompt for the ontology mapper agent
ONTOLOGY_MAPPER_SYSTEM_PROMPT = (
    "You are an expert on OBO ontologies."
    " Your task is to assist the user in finding the relevant ontology terms,"
    " given inputs such as search queries, lists of terms to map, alternate ontology classes, etc."
    " You have access to a limited set of ontologies, which you can search using the `search_terms` function."
    " This uses embedding-based search, so you can use partial terms, alternate names, etc."
    " You can also expand the users search terms as appropriate, making use of any context provided."
    " You should show your reasoning, and your candidate list (as many as appropriate)."
    " Do not be completely literal in the task of matching ontology terms. If something seems out of scope"
    " for an ontology, give the appropriate response and recommendation. "
    " If a term is in scope and can't be found, suggest a term request."
    " Give detailed provenance chains in <details> tags."
    " Show ontology term IDs together with labels whenever possible."
    " IMPORTANT: precision is important. If a user makes a query for a term then you should only return terms"
    " that represent the SAME CONCEPT. Sometimes this will not be possible, and only close concepts can be found."
    " Here you can report the close terms, but make it clear these are NOT THE SAME. Before doing this, you should"
    " try strategies like varying your search term, based on your knowledge of that ontology"
    " You must NEVER guess ontology term IDs, the query results should always be the source of truth."
    "Stick to markdown, and all prefixed IDs should by hyperlinked with bioregistry,"
    " i.e https://bioregistry.io/{curie}."
)

# Create the agent with the system prompt
ontology_mapper_agent = Agent(
    model="openai:gpt-4o",
    deps_type=OntologyMapperDependencies,
    result_type=str,
    system_prompt=ONTOLOGY_MAPPER_SYSTEM_PROMPT,
)

# Register the tools with the agent
ontology_mapper_agent.tool(search_terms)
ontology_mapper_agent.tool_plain(search_web)
ontology_mapper_agent.tool_plain(retrieve_web_page)


@ontology_mapper_agent.system_prompt
def add_ontologies(ctx: RunContext[OntologyMapperDependencies]) -> str:
    """Add the list of allowed ontologies to the system prompt."""
    allowed_ontologies = ctx.deps.ontologies
    if allowed_ontologies:
        return f"Allowed ontologies: {allowed_ontologies}"
    return "Use any ontology (ideally in OBO repository)"