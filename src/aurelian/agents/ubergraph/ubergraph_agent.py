"""
Agent for working with ontologies via UberGraph endpoint.
"""
from typing import Dict

from pydantic_ai import Agent, RunContext

from .ubergraph_config import Dependencies, get_config
from .ubergraph_tools import query_ubergraph

# Assumptions about the UberGraph data model
ASSUMPTIONS = {
    "provenance": (
        "When formulating your response to tool outputs,",
        " you can extemporize with your own knowledge, but if you do so,"
        " you must be clear about which statements come from the ontology"
        " vs your own knowledge.",
    ),
    "ids": "include both IDs and labels in responses, unless directed not to do so.",
    "obo": "Assume OBO style ontology and OBO PURLs (http://purl.obolibrary.org/obo/).",
    "rg": (
        "All edges are stored as simple triples, e.g CL:0000080 BFO:0000050 UBERON:0000179"
        " for 'circulating cell' 'part of' 'haemolymphatic fluid'"
    ),
    "ont_graph": (
        "Direct (asserted) edges are stored in the `renci:ontology` graph." "Use this by default, even for subClassOf."
    ),
    "entailed": (
        "Indirect (entailed) edges (including reflexive) are stored in the `renci:redundant` graph"
        "Use this for queries that require transitive closure, e.g. rdfs:subClassOf+"
        "Note however that other triples like rdfs:label are NOT in this graph - use renci:ontology for these."
    ),
    "paths": "In general you should NOT use paths like rdfs:subClassOf+, use the entailed graph.",
    "ro": "RO is used for predicates. Common relations include BFO:0000050 for part-of.",
    "is_a": "rdfs:subClassOf is used for is_a relationships.",
    "labels": "rdfs:label used for labels. IDs/URIs are typically OBO-style.",
    "oboInOwl": "assume obiInOwl for synonyms, e.g. oboInOwl:hasExactSynonym.",
    "blazegraph": (
        "Blazegraph is used as the underlying triplestore."
        "This means you SHOULD do relevance-ranked match queries over CONTAINS. "
        "E.g. ?c rdfs:label ?v . ?v bds:search 'circulating cell' ; ?v bds:relevance ?score ."
    ),
    "def": "IAO:0000115 is used for definitions.",
    "xref": "assume oboInOwl:hasDbXref for simple cross-references.",
    "mixed_language": "Do not assume all labels are language tagged.",
}

# Create the UberGraph agent
ubergraph_agent = Agent(
    "openai:gpt-4o",
    deps_type=Dependencies,
    result_type=str,
)

# Register tools
ubergraph_agent.tool(query_ubergraph)


@ubergraph_agent.system_prompt
def add_ontology_assumptions(ctx: RunContext[Dependencies]) -> str:
    """Add ontology assumptions to the system prompt."""
    return "\n\n" + "\n\n".join([f"Assumption: {desc}" for name, desc in ASSUMPTIONS.items()])


@ubergraph_agent.system_prompt
def add_prefixes(ctx: RunContext[Dependencies]) -> str:
    """Add SPARQL prefixes to the system prompt."""
    prefixes = ctx.deps.prefixes
    return "\n\nAssume the following prefixes are auto-included:" + "\n".join(
        [f"\nPrefix: {prefix}: {expansion}" for prefix, expansion in prefixes.items()]
    )