from dataclasses import dataclass, field
from typing import Any, Dict, List

from oaklib import get_adapter
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from SPARQLWrapper import JSON, SPARQLWrapper

UBERGRAPH_ENDPOINT = "https://ubergraph.apps.renci.org/sparql"

DEFAULT_PREFIXES = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "obo": "http://purl.obolibrary.org/obo/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "renci": "http://reasoner.renci.org/",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
    "BFO": "http://purl.obolibrary.org/obo/BFO_",
    "RO": "http://purl.obolibrary.org/obo/RO_",
    "GO": "http://purl.obolibrary.org/obo/GO_",
    "SO": "http://purl.obolibrary.org/obo/SO_",
    "CHEBI": "http://purl.obolibrary.org/obo/CHEBI_",
    "CL": "http://purl.obolibrary.org/obo/CL_",
    "UBERON": "http://purl.obolibrary.org/obo/UBERON_",
    "IAO": "http://purl.obolibrary.org/obo/IAO_",
    "OBI": "http://purl.obolibrary.org/obo/OBI_",
    "biolink": "https://w3id.org/biolink/vocab/",
    "bds": "http://www.bigdata.com/rdf/search#",
}

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

adapter = get_adapter("sqlite:obo:cl")


@dataclass
class Dependencies:
    prefixes: Dict[str, str] = field(default_factory=lambda: DEFAULT_PREFIXES)


class QueryResults(BaseModel):
    results: List[Dict] = []


def simplify_value(v: Dict, prefixes=None) -> Any:
    if prefixes and v["type"] == "uri":
        for prefix, expansion in prefixes.items():
            if v["value"].startswith(expansion):
                return f"{prefix}:{v['value'][len(expansion):]}"
    return v["value"]


def simplify_results(results: Dict, prefixes=None, limit=20) -> List[Dict]:
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


ubergraph_agent = Agent(
    "openai:gpt-4o",
    deps_type=Dependencies,
    result_type=str,
)


@ubergraph_agent.system_prompt
def add_ontology_assumptions(ctx: RunContext[Dependencies]) -> str:
    return "\n\n" + "\n\n".join([f"Assumption: {desc}" for name, desc in ASSUMPTIONS.items()])


@ubergraph_agent.system_prompt
def add_prefixes(ctx: RunContext[Dependencies]) -> str:
    prefixes = ctx.deps.prefixes
    return "\n\nAssume the following prefixes are auto-included:" + "\n".join(
        [f"\nPrefix: {prefix}: {expansion}" for prefix, expansion in prefixes.items()]
    )


@ubergraph_agent.tool
def query_ubergraph(ctx: RunContext[Dependencies], query: str) -> QueryResults:
    """Performs a SPARQL query over Ubergraph then returns the results as triples.

    Ubergraph is a triplestore that contains many OBO ontologies and precomputed
    relation graph edges.
    """
    prefixes = ctx.deps.prefixes
    sw = SPARQLWrapper(UBERGRAPH_ENDPOINT)
    for k, v in prefixes.items():
        query = f"PREFIX {k}: <{v}>\n" + query
    print("## Query")
    print(query)
    print("##")
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    # check_limit()
    ret = sw.queryAndConvert()
    results = simplify_results(ret, prefixes)
    print("num results=", len(results))
    print("results=", results)
    qr = QueryResults(results=results)
    print("qr=", qr)
    return qr
