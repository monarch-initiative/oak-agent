"""
Agent for interacting with GO KnowledgeBase via AmiGO solr endpoint.
"""
from aurelian.agents.amigo.amigo_config import AmiGODependencies
from aurelian.agents.amigo.amigo_tools import (
    find_gene_associations,
    find_gene_associations_for_pmid,
    lookup_uniprot_entry,
    uniprot_mapping
)
from aurelian.agents.literature.literature_tools import (
    lookup_pmid as literature_lookup_pmid,
    search_literature_web,
    retrieve_literature_page
)
from pydantic_ai import Agent, Tool

SYSTEM = """
You are a biocurator that can answer questions using the Gene Ontology knowledge base via the AmiGO API.

Do not assume the knowledge base is complete or always correct. Your job is to help curators find mistakes
or missing information. A particular pervasive issue in GO is over-annotation based on phenotypes - a gene
should only be annotated to a process if it is involved in that process, i.e., if the activity of the
gene process is an identifiable step in the pathway.

You can help with:
- Finding gene associations for specific genes or gene products
- Finding gene associations cited in specific publications by PMID
- Looking up protein information via UniProt
- Mapping UniProt accessions to other databases
- Analyzing gene function and involvement in biological processes
- Identifying potential over-annotations or missing annotations

You can also use your general knowledge of genes and biological processes, and do additional searches
when needed to provide context or verification.
"""

amigo_agent = Agent(
    model="openai:gpt-4o",
    deps_type=AmiGODependencies,
    system_prompt=SYSTEM,
    tools=[
        Tool(find_gene_associations),
        Tool(find_gene_associations_for_pmid),
        Tool(lookup_uniprot_entry),
        Tool(uniprot_mapping),
        Tool(literature_lookup_pmid, name="lookup_pmid",
             description="""Lookup the text of a PubMed article by its PMID.

A PMID should be of the form "PMID:nnnnnnn" (no underscores).

This is useful for retrieving the full text of papers referenced in GO annotations
to verify the evidence for gene annotations or identify potential over-annotations.

Args:
    pmid: The PubMed ID to look up
        
Returns:
    str: Full text if available, otherwise abstract"""),
        Tool(search_literature_web, name="search_web",
             description="""Search the web using a text query.
    
Args:
    query: The search query
        
Returns:
    str: Search results with summaries"""),
        Tool(retrieve_literature_page, name="retrieve_web_page",
             description="""Fetch the contents of a web page.
    
Args:
    url: The URL to fetch
        
Returns:
    str: The contents of the web page""")
    ]
)