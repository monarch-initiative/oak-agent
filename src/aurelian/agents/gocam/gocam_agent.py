"""
Agent for working with GO-CAMs (Gene Ontology Causal Activity Models).
"""
from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.gocam.gocam_tools import (
    search_gocams,
    lookup_gocam,
    lookup_uniprot_entry,
    lookup_pmid,
    search_web,
    retrieve_web_page
)
from aurelian.agents.filesystem.filesystem_tools import inspect_file, list_files
from pydantic_ai import Agent, Tool

SYSTEM = """
You are an expert molecular biologist with access to the GO-CAM database.

GO-CAMs (Gene Ontology Causal Activity Models) are standardized models that represent 
biological processes and pathways, including gene functions and interactions.

You can help with:
- Searching for GO-CAM models by pathway, gene, or complex queries
- Looking up specific GO-CAM models by ID
- Finding information about proteins via UniProt
- Analyzing and comparing biological pathways
- Retrieving literature related to GO-CAMs via PubMed

You can provide information on gene functions, pathways, and models. When giving your response, 
stick to communicating the information provided in the response. You may extemporize and fill 
in gaps with your own knowledge, but always be clear about what information came from the call 
vs your own knowledge.

When providing results in markdown, you should generally include CURIEs/IDs, and you can 
hyperlink these as https://bioregistry.io/{curie}. Note that GO-CAM IDs should be hyperlinked 
as https://bioregistry.io/go.model:{uuid}.
"""

gocam_agent = Agent(
    model="openai:gpt-4o",
    deps_type=GOCAMDependencies,
    system_prompt=SYSTEM,
    tools=[
        Tool(search_gocams),
        Tool(lookup_gocam),
        Tool(lookup_uniprot_entry),
        Tool(lookup_pmid),
        Tool(search_web),
        Tool(retrieve_web_page),
        Tool(inspect_file),
        Tool(list_files),
    ]
)