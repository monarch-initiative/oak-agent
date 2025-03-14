"""Command line interface for Aurelian agents."""

import logging
from typing import Optional, List

import click

from aurelian import __version__

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


def parse_multivalued(ctx, param, value: Optional[str]) -> Optional[List]:
    """Parse a comma-separated string into a list."""
    if not value:
        return None
    return value.split(',') if isinstance(value, str) and ',' in value else [value]


# Common CLI options
model_option = click.option(
    "--model",
    "-m",
    help="The model to use for the agent.",
)
workdir_option = click.option(
    "--workdir",
    "-w",
    default="workdir",
    show_default=True,
    help="The working directory for the agent.",
)
share_option = click.option(
    "--share/--no-share",
    default=False,
    show_default=True,
    help="Share the agent GradIO UI via URL.",
)
ui_option = click.option(
    "--ui/--no-ui",
    default=False,
    show_default=True,
    help="Start the agent in UI mode instead of direct query mode.",
)
ontologies_option = click.option(
    "--ontologies",
    "-i",
    callback=parse_multivalued,
    help="Comma-separated list of ontologies to use for the agent.",
)
server_port_option = click.option(
    "--server-port",
    "-p",
    default=7860,
    show_default=True,
    help="The port to run the UI server on.",
)
db_path_option = click.option(
    "--db-path",
    "-d",
    help="The path to the database.",
)
collection_name_option = click.option(
    "--collection-name",
    "-c",
    help="The name of the collection.",
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """Main command for Aurelian.

    Aurelian provides a collection of specialized agents for various scientific and biomedical tasks.
    Each agent can be run in either direct query mode or UI mode:
    
    - Direct query mode: Run the agent with a query (e.g., `aurelian diagnosis "patient with hypotonia"`).
    - UI mode: Run the agent with `--ui` flag to start a chat interface.
    
    Some agents also provide utility commands for specific operations.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)
    import logfire

    logfire.configure()


def split_options(kwargs, agent_keys: Optional[List]=None, extra_agent_keys: Optional[List] = None):
    """Split options into agent and launch options."""
    if agent_keys is None:
        agent_keys = ["model", "workdir", "ontologies", "db_path", "collection_name"]
    if extra_agent_keys is not None:
        agent_keys += extra_agent_keys
    agent_options = {k: v for k, v in kwargs.items() if k in agent_keys}
    launch_options = {k: v for k, v in kwargs.items() if k not in agent_keys}
    return agent_options, launch_options


def run_agent(
    agent_name: str, 
    agent_module: str, 
    query: Optional[tuple] = None, 
    ui: bool = False, 
    agent_func_name: str = "run_sync",
    join_char: str = " ",
    **kwargs
) -> None:
    """Run an agent in either UI or direct query mode.
    
    Args:
        agent_name: Agent's name for import paths
        agent_module: Fully qualified module path to the agent
        query: Text query for direct mode
        ui: Whether to force UI mode
        agent_func_name: Name of the function to run the agent
        join_char: Character to join multi-part queries with
        kwargs: Additional arguments for the agent
    """
    # Import required modules
    # These are imported dynamically to avoid loading all agents on startup
    gradio_module = __import__(f"aurelian.agents.{agent_name}.{agent_name}_gradio", fromlist=["chat"])
    agent_class = __import__(f"aurelian.agents.{agent_name}.{agent_name}_agent", fromlist=[f"{agent_name}_agent"])
    config_module = __import__(f"aurelian.agents.{agent_name}.{agent_name}_config", fromlist=["get_config"])
    
    chat_func = gradio_module.chat
    agent = getattr(agent_class, f"{agent_name}_agent")
    get_config = config_module.get_config
    
    # Process agent and UI options
    agent_keys = ["model", "workdir", "ontologies", "db_path", "collection_name"]
    agent_options, launch_options = split_options(kwargs, agent_keys=agent_keys)
    
    # Run in appropriate mode
    if not ui and query:
        # Direct query mode
        deps = get_config()
        
        # Set workdir if provided
        if 'workdir' in agent_options and agent_options['workdir']:
            if hasattr(deps, 'workdir'):
                deps.workdir.location = agent_options['workdir']
        
        # Remove workdir from agent options to avoid duplicates
        agent_run_options = {k: v for k, v in agent_options.items() if k != 'workdir'}
        
        # Run the agent and print results
        r = getattr(agent, agent_func_name)(join_char.join(query), deps=deps, **agent_run_options)
        print(r.data)
    else:
        # UI mode
        gradio_ui = chat_func(**agent_options)
        gradio_ui.launch(**launch_options)


@main.command()
def gocam_ui():
    """Start the GO-CAM UI (non-chat interface)."""
    from aurelian.agents.gocam.gocam_gradio import ui
    
    gocam_ui = ui()
    gocam_ui.launch()


@main.command()
@click.option("--limit", "-l", default=10, show_default=True, help="Number of results to return.")
@click.argument("ontology")
@click.argument("term")
def search_ontology(ontology: str, term: str, **kwargs):
    """Search the ontology for the given query term.

    Also has side effect of indexing. You may want to pre-index before
    starting an individual UI.
    """
    import aurelian.utils.ontology_utils as ontology_utils
    from oaklib import get_adapter

    handle = "sqlite:obo:" + ontology
    adapter = get_adapter(handle)
    objs = ontology_utils.search_ontology(adapter, term, **kwargs)
    for id, label in objs:
        print(id, label)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def gocam(ui, query, **kwargs):
    """Start the GO-CAM Agent for gene ontology causal activity models.
    
    The GO-CAM Agent helps create and analyze Gene Ontology Causal Activity Models,
    which describe biological systems as molecular activities connected by causal 
    relationships. 
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("gocam", "aurelian.agents.gocam", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def phenopackets(ui, query, **kwargs):
    """Start the Phenopackets Agent for standardized phenotype data.
    
    The Phenopackets Agent helps work with GA4GH Phenopackets, a standard 
    format for sharing disease and phenotype information for genomic 
    medicine.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("phenopackets", "aurelian.agents.phenopackets", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def diagnosis(ui, query, **kwargs):
    """Start the Diagnosis Agent for rare disease diagnosis.
    
    The Diagnosis Agent assists in diagnosing rare diseases by leveraging the 
    Monarch Knowledge Base. It helps clinical geneticists evaluate potential 
    conditions based on patient phenotypes.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("diagnosis", "aurelian.agents.diagnosis", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def checklist(ui, query, **kwargs):
    """Start the Checklist Agent for paper evaluation.
    
    The Checklist Agent evaluates scientific papers against established checklists 
    such as STREAMS, STORMS, and ARRIVE. It helps ensure that papers conform to 
    relevant reporting guidelines and best practices.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("checklist", "aurelian.agents.checklist", query=query, ui=ui, **kwargs)


# Keep backward compatibility
@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def aria(**kwargs):
    """Start the Checklist UI (deprecated, use 'checklist' instead)."""
    run_agent("checklist", "aurelian.agents.checklist", ui=True, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def linkml(ui, query, **kwargs):
    """Start the LinkML Agent for data modeling and schema validation.
    
    The LinkML Agent helps create and validate data models and schemas using the 
    Linked data Modeling Language (LinkML). It can assist in generating schemas,
    validating data against schemas, and modeling domain knowledge.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("linkml", "aurelian.agents.linkml", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def robot(ui, query, **kwargs):
    """Start the ROBOT Agent for ontology operations.
    
    The ROBOT Agent provides natural language access to ontology operations 
    and manipulations using the ROBOT tool. It can create, modify, and analyze
    ontologies through a chat interface.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("robot", "aurelian.agents.robot", query=query, ui=ui, agent_func_name="chat", **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def amigo(ui, query, **kwargs):
    """Start the AmiGO Agent for Gene Ontology data exploration.
    
    The AmiGO Agent provides access to the Gene Ontology (GO) and gene 
    product annotations. It helps users explore gene functions and 
    ontology relationships.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("amigo", "aurelian.agents.amigo", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@db_path_option
@collection_name_option
@click.argument("query", nargs=-1, required=False)
def rag(ui, query, db_path, collection_name, **kwargs):
    """Start the RAG Agent for document retrieval and generation.
    
    The RAG (Retrieval-Augmented Generation) Agent provides a natural language 
    interface for exploring and searching document collections. It uses RAG 
    techniques to combine search capabilities with generative AI.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    if not db_path:
        click.echo("Error: --db-path is required")
        return
    
    # Add special parameters to kwargs
    kwargs["db_path"] = db_path
    if collection_name:
        kwargs["collection_name"] = collection_name
        
    run_agent("rag", "aurelian.agents.rag", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@ontologies_option
@click.argument("query", nargs=-1, required=False)
def mapper(ui, query, ontologies, **kwargs):
    """Start the Ontology Mapper Agent for mapping between ontologies.
    
    The Ontology Mapper Agent helps translate terms between different ontologies
    and vocabularies. It can find equivalent concepts across ontologies and 
    explain relationships.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    # Special handling for ontologies parameter
    if ontologies:
        if isinstance(ontologies, str):
            ontologies = [ontologies]
        kwargs["ontologies"] = ontologies
        
    run_agent("ontology_mapper", "aurelian.agents.ontology_mapper", query=query, ui=ui, join_char="\n", **kwargs)


@main.command()
@click.argument("pmid")
def fulltext(pmid):
    """Download full text for a PubMed article."""
    from aurelian.utils.pubmed_utils import get_pmid_text
    txt = get_pmid_text(pmid)
    print(txt)


@main.command()
@click.argument("term")
def websearch(term):
    """Search the web for a query term."""
    from aurelian.utils.search_utils import web_search
    txt = web_search(term)
    print(txt)


@main.command()
@click.argument("url")
def geturl(url):
    """Retrieve content from a URL."""
    from aurelian.utils.search_utils import retrieve_web_page
    txt = retrieve_web_page(url)
    print(txt)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("url", required=False)
def datasheets(ui, url, **kwargs):
    """Start the Datasheets for Datasets (D4D) Agent.
    
    The D4D Agent extracts structured metadata from dataset documentation
    according to the Datasheets for Datasets schema. It can analyze both 
    web pages and PDF documents describing datasets.
    
    Run with a URL for direct mode or with --ui for interactive chat mode.
    """
    run_agent("d4d", "aurelian.agents.d4d", query=(url,) if url else None, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def chemistry(ui, query, **kwargs):
    """Start the Chemistry Agent for chemical structure analysis.
    
    The Chemistry Agent helps interpret and work with chemical structures,
    formulas, and related information.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("chemistry", "aurelian.agents.chemistry", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def literature(ui, query, **kwargs):
    """Start the Literature Agent for scientific publication analysis.
    
    The Literature Agent provides tools for analyzing scientific publications,
    extracting key information, and answering questions about research articles.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("literature", "aurelian.agents.literature", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def biblio(ui, query, **kwargs):
    """Start the Biblio Agent for bibliographic data management.
    
    The Biblio Agent helps organize and search bibliographic data and citations. 
    It provides tools for searching a bibliography database, retrieving scientific 
    publications, and accessing web content.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("biblio", "aurelian.agents.biblio", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def monarch(ui, query, **kwargs):
    """Start the Monarch Agent for biomedical knowledge exploration.
    
    The Monarch Agent provides access to relationships between genes, diseases, 
    phenotypes, and other biomedical entities through the Monarch Knowledge Base.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("monarch", "aurelian.agents.monarch", query=query, ui=ui, **kwargs)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@ui_option
@click.argument("query", nargs=-1, required=False)
def ubergraph(ui, query, **kwargs):
    """Start the UberGraph Agent for SPARQL-based ontology queries.
    
    The UberGraph Agent provides a natural language interface to query ontologies 
    using SPARQL through the UberGraph endpoint. It helps users formulate and execute
    SPARQL queries without needing to know the full SPARQL syntax.
    
    Run with a query for direct mode or with --ui for interactive chat mode.
    """
    run_agent("ubergraph", "aurelian.agents.ubergraph", query=query, ui=ui, **kwargs)


@main.command(name="scientific_knowledge")
@model_option
@workdir_option
@share_option
@server_port_option
@click.option("--pdf-dir", "-p", help="The directory containing PDF files to process")
@click.option("--cache-dir", "-c", help="The directory to use for caching extracted knowledge")
def scientific_knowledge(pdf_dir, cache_dir, **kwargs):
    """Start the Scientific Knowledge Extraction Agent UI.
    
    The Scientific Knowledge Extraction Agent extracts structured knowledge from scientific 
    papers in PDF format. It identifies key findings, relations, and claims, and maps them 
    to standard ontology terms, providing full provenance tracking to the source evidence.
    
    Features:
    - Extract structured assertions (subject-predicate-object) from scientific papers
    - Map extracted concepts to standard ontologies (GO, ChEBI, DOID, etc.)
    - Export assertions as CSV, JSON, or RDF with full provenance
    - Maintain a cache of processed papers to avoid redundant work
    """
    from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_gradio import create_demo
    from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
    
    agent_options, launch_options = split_options(kwargs)
    
    # Create the Gradio demo
    demo = create_demo()
    
    # If PDF directory was provided, set it up first
    if pdf_dir:
        # Import setup_directories function for initialization
        from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_gradio import setup_directories
        
        # Initialize the PDF directory before starting the UI
        setup_result = setup_directories(pdf_dir, cache_dir)
        print(f"Scientific Knowledge Extraction Agent: {setup_result}")
    
    # Launch with the appropriate options
    demo.launch(**launch_options)
    
@main.command(name="ske")
@model_option
@workdir_option
@share_option
@server_port_option
@click.option("--pdf-dir", "-p", help="The directory containing PDF files to process")
@click.option("--cache-dir", "-c", help="The directory to use for caching extracted knowledge")
def ske_alias(pdf_dir, cache_dir, **kwargs):
    """Alias for scientific_knowledge - Scientific Knowledge Extraction Agent UI."""
    # Instead of calling scientific_knowledge directly, implement the same functionality here
    from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_gradio import create_demo
    from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
    
    agent_options, launch_options = split_options(kwargs)
    
    # Create the Gradio demo
    demo = create_demo()
    
    # If PDF directory was provided, set it up first
    if pdf_dir:
        # Import setup_directories function for initialization
        from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_gradio import setup_directories
        
        # Initialize the PDF directory before starting the UI
        setup_result = setup_directories(pdf_dir, cache_dir)
        print(f"Scientific Knowledge Extraction Agent: {setup_result}")
    
    # Launch with the appropriate options
    demo.launch(**launch_options)


@main.command(name="ske_clear_cache")
@click.option("--pdf-dir", "-p", required=True, help="The directory containing PDF files whose cache should be cleared")
@click.option("--cache-dir", "-c", help="The directory used for caching extracted knowledge")
@click.option("--file", "-f", help="Specific PDF file to clear from the cache. If not provided, clears all cached files.")
def clear_scientific_knowledge_cache(pdf_dir, cache_dir, file):
    """Clear the Scientific Knowledge Extraction Agent's cache.
    
    This command clears the extracted knowledge cache for the Scientific Knowledge Extraction Agent.
    You can clear the cache for a specific file or for all processed files.
    
    Args:
        pdf_dir: The directory containing the PDF files (required)
        cache_dir: Optional custom cache directory
        file: Optional specific PDF file to clear from cache
    """
    from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
    
    # Create dependencies with the specified directories
    deps = ScientificKnowledgeExtractionDependencies(
        pdf_directory=pdf_dir,
        cache_directory=cache_dir
    )
    
    if file:
        # Clear specific file
        file_path = os.path.join(pdf_dir, file) if not os.path.isabs(file) else file
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return
            
        entries = deps.clear_cache(file_path)
        if entries > 0:
            print(f"Successfully cleared cache for '{os.path.basename(file_path)}'.")
        else:
            print(f"File '{os.path.basename(file_path)}' was not in the cache.")
    else:
        # Clear all
        entries = deps.clear_cache()
        if entries > 0:
            print(f"Successfully cleared the entire cache ({entries} entries).")
        else:
            print("Cache was already empty.")


# DO NOT REMOVE THIS LINE
# added this for mkdocstrings to work
# see https://github.com/bruce-szalwinski/mkdocs-typer/issues/18
#click_app = get_command(app)
#click_app.name = "aurelian"

if __name__ == "__main__":
    main()
