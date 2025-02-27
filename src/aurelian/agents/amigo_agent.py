from dataclasses import dataclass
from typing import Dict, List

from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import obj_to_dict
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search
from bioservices import UniProt
from oaklib import get_adapter
from oaklib.datamodels.association import Association, NegatedAssociation
from oaklib.implementations import AmiGOImplementation
from oaklib.implementations.amigo.amigo_implementation import DEFAULT_SELECT_FIELDS, QUALIFIER, BIOENTITY, \
    BIOENTITY_LABEL, map_predicate, ANNOTATION_CLASS, ANNOTATION_CLASS_LABEL, REFERENCE, EVIDENCE_TYPE, ASSIGNED_BY
from pydantic_ai import Agent, RunContext

from aurelian.agents.uniprot_agent import normalize_uniprot_id
from aurelian.utils.data_utils import obj_to_dict

u = UniProt()


@dataclass
class AmiGODependencies:
    taxon: str = "9606"


amigo_agent = Agent(
    model="openai:gpt-4o",
    system_prompt="""
    You are an biocurator that can answer questions using the Gene Ontology knowledge base via the AmiGO API.
    Do not assume the knowledge base is complete or always correct. Your job is to help curators find mistakes
    or missing information. A particular pervasive issue in GO is over-annotation based on phenotypes - a gene
    should only be annotated to a process if it is involved in that process, i.e. if the activity of the
    gene process is an identifiable step in the pathway.
    
    You can also use your general knowledge of the genes involved, and do additional searches.
    
    You can use the following tools:
    
    - `find_gene_associations` to find gene associations for a given gene or gene product
    - `find_gene_associations_by_pmid` to find gene associations by a PMID
    - `retrieve_web_page` to fetch the contents of a web page
    - `search_web` to search the web using a text query
    - `lookup_pmid` to lookup the text of a PubMed ID
    """
)


def get_amigo_adapter(ctx: RunContext[AmiGODependencies]) -> AmiGOImplementation:
    taxon = ctx.deps.taxon
    return get_adapter(f"amigo:NCBITaxon:{taxon}")


def get_gene_id(ctx: RunContext[AmiGODependencies], gene_term: str) -> str:
    return gene_term

def normalize_pmid(pmid: str) -> str:
    if ":" in pmid:
        pmid = pmid.split(":", 1)[1]
    if not pmid.startswith("PMID:"):
        pmid = f"PMID:{pmid}"
    return pmid


def gene_associations(ctx: RunContext[AmiGODependencies], gene_id: str) -> List[Dict]:
    """Retrieve gene associations for a given gene

    Args:
        ctx: The run context
        gene_id: The gene ID

    """
    print(f"GENE: {gene_id}")
    adapter = get_amigo_adapter(ctx)
    normalized_gene_id = get_gene_id(ctx, gene_id)
    assocs = [obj_to_dict(a) for a in adapter.associations([normalized_gene_id])]
    return assocs

def gene_associations_for_pmid(amigo: AmiGOImplementation, pmid: str) -> List[Dict]:
    """
    Find gene associations for a given PMID

    Args:
        ctx:
        pmid: The PMID

    Returns:

    """
    print(f"Lookup amigo annotations to PMID: {pmid}")
    from oaklib.implementations.amigo.amigo_implementation import _query as amigo_query
    from oaklib.implementations.amigo.amigo_implementation import _normalize
    solr = amigo._solr
    select_fields = DEFAULT_SELECT_FIELDS
    results = amigo_query(solr, {"reference": pmid}, select_fields)
    assocs = []
    for doc in results:
        cls = Association
        quals = set(doc.get(QUALIFIER, []))
        if "not" in quals:
            cls = NegatedAssociation
        assoc = cls(
            subject=_normalize(doc[BIOENTITY]),
            subject_label=doc[BIOENTITY_LABEL],
            predicate=map_predicate(quals),
            negated=cls == NegatedAssociation,
            object=doc[ANNOTATION_CLASS],
            object_label=doc[ANNOTATION_CLASS_LABEL],
            publications=doc[REFERENCE],
            evidence_type=doc.get(EVIDENCE_TYPE),
            primary_knowledge_source=doc[ASSIGNED_BY],
            aggregator_knowledge_source="infores:go",
        )
        assocs.append(obj_to_dict(assoc))
    return assocs

@amigo_agent.tool
def find_gene_associations(ctx: RunContext[AmiGODependencies], gene_id: str) -> List[Dict]:
    """
    Find gene associations for a given gene or gene prodict.

    Args:
        ctx:
        gene_id: gene or gene product IDs

    Returns:

    """
    return gene_associations(ctx, gene_id)


@amigo_agent.tool
def find_gene_associations_for_pmid(ctx: RunContext[AmiGODependencies], pmid: str) -> List[Dict]:
    """
    Find gene associations for a given PMID

    Args:
        ctx:
        pmid: The PMID

    Returns:

    """
    pmid = normalize_pmid(pmid)
    amigo = get_amigo_adapter(ctx)
    return gene_associations_for_pmid(amigo, pmid)


@amigo_agent.tool
def lookup_uniprot_entry(ctx: RunContext[AmiGODependencies], uniprot_acc: str) -> str:
    """Lookup the Uniprot entry for a given Uniprot accession number

    Args:
        uniprot_acc: The Uniprot accession

    """
    uniprot_acc = normalize_uniprot_id(uniprot_acc)
    return u.retrieve(uniprot_acc, frmt="txt")


@amigo_agent.tool
def uniprot_mapping(ctx: RunContext[AmiGODependencies], target_database: str, uniprot_accs: List[str]) -> Dict:
    """Perform a mapping of Uniprot accessions to another database

    Args:
        target_database: The target database (e.g KEGG, PDB)
        uniprot_accs: The Uniprot accessions

    """
    uniprot_accs = [normalize_uniprot_id(x) for x in uniprot_accs]
    return u.mapping("UniProtKB_AC-ID", target_database, ",".join(uniprot_accs))


@amigo_agent.tool_plain()
def search_web(query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@amigo_agent.tool_plain
def retrieve_web_page(url: str) -> str:
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


@amigo_agent.tool_plain
def lookup_pmid(pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    A PMID should be of the form "PMID:nnnnnnn" (no underscores).


    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    return get_pmid_text(pmid)


def chat(**kwargs):
    import gradio as gr
    deps = AmiGODependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: amigo_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="AmiGO AI Assistant",
        examples=[
            ["What are some annotations for the protein UniProtKB:Q9UMS5"],
            ["Check PMID:19661248 for over-annotation"],
        ]
    )
