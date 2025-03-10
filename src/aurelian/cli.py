"""Command line interface for ubergraph-agent."""

import logging
from typing import Optional, List

import click

from aurelian import __version__

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


def parse_multivalued(ctx, param, value: Optional[str]) -> Optional[List]:
    if not value:
        return None
    return value.split(',') if isinstance(value, str) and ',' in value else [value]


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
    help="Share the agent GradIO chat via URL.",
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
    help="The port to run the gradio server on.",
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

    THIS CLI MAY CHANGE.

    Currently there are multiple sub-commands,
    each of which starts a UI for an agent.

    However, there are a few other utility commands,
    e.g. for indexing an ontology or downloading a PMID

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


def split_options3(kwargs, agent_keys: Optional[List]=None, extra_agent_keys: Optional[List] = None, launch_keys: Optional[List] = None):
    """Split options into deps, agent, and agent options."""
    if launch_keys is None:
        launch_keys = ["server_port", "share"]
    if agent_keys is None:
        agent_keys = ["model"]
    if extra_agent_keys is not None:
        agent_keys += extra_agent_keys
    agent_options = {k: v for k, v in kwargs.items() if k in agent_keys}
    launch_options = {k: v for k, v in kwargs.items() if k in launch_keys}
    deps_options = {k: v for k, v in kwargs.items() if k not in agent_keys and k not in launch_keys}
    return deps_options, agent_options, launch_options


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
@share_option
@server_port_option
def gocam(share: bool, server_port: Optional[int] = None, **kwargs):
    """Start the GO-CAM Chat UI."""
    from aurelian.agents.gocam.gocam_gradio import chat
    
    agent_options, launch_options = split_options(kwargs)
    ui = chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
def phenopackets(**kwargs):
    """Start the Phenopackets Agent for exploring phenopacket databases."""
    from aurelian.agents.phenopackets.phenopackets_gradio import chat
    agent_options, launch_options = split_options(kwargs)
    ui = chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
@click.argument("query", nargs=-1)
def diagnosis(**kwargs):
    """Start the diagnosis agent."""
    import aurelian.agents.diagnosis_agent as diagnosis

    agent_options, launch_options = split_options(kwargs)
    ui = diagnosis.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
def aria(share: bool, server_port: Optional[int] = None, **kwargs):
    """Start the Checklist UI."""
    import aurelian.agents.checklist_agent as aria

    ui = aria.chat(**kwargs)
    ui.launch(share=share, server_port=server_port)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def linkml(**kwargs):
    """Start the LinkML agent."""
    import aurelian.agents.linkml.linkml_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def robot(**kwargs):
    """Start the robot ontology agent."""
    import aurelian.agents.robot.robot_ontology_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
def amigo(**kwargs):
    """Start the AmiGO agent for working with Gene Ontology."""
    from aurelian.agents.amigo.amigo_gradio import chat
    agent_options, launch_options = split_options(kwargs)
    ui = chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@db_path_option
@collection_name_option
@server_port_option
def rag(**kwargs):
    """Start the AmiGO agent."""
    import aurelian.agents.rag_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
    ui.launch(**launch_options)

@main.command()
@model_option
@share_option
@server_port_option
@ontologies_option
@click.argument("query", nargs=-1)
def mapper(query, ontologies, **kwargs):
    """Start the Ontology Mapper agent."""
    from aurelian.agents.ontology_mapper.ontology_mapper_agent import ontology_mapper_agent
    from aurelian.agents.ontology_mapper.ontology_mapper_config import OntologyMapperDependencies, get_config
    from aurelian.agents.ontology_mapper.ontology_mapper_gradio import chat
    
    # Create appropriate dependencies
    if ontologies:
        if isinstance(ontologies, str):
            ontologies = [ontologies]
        deps = get_config(ontologies=ontologies)
    else:
        deps = get_config()
        
    deps_options, agent_options, launch_options = split_options3(kwargs)
    
    if query:
        r = ontology_mapper_agent.run_sync("\n".join(query), deps=deps)
        print(r.data)
    else:
        ui = chat(deps, **agent_options)
        ui.launch(**launch_options)


@main.command()
@click.argument("pmid")
def fulltext(pmid):
    """Download full text."""
    from aurelian.utils.pubmed_utils import get_pmid_text
    txt = get_pmid_text(pmid)
    print(txt)


@main.command()
@model_option
@share_option
@server_port_option
def datasheets(**kwargs):
    """Start the Data Sheets Metadata Agent."""
    import aurelian.agents.d4d_agent as datasheets_agent
    agent_options, launch_options = split_options(kwargs)
    ui = datasheets_agent.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def chemistry(**kwargs):
    """Start the Chemistry Agent for working with chemical structures."""
    from aurelian.agents.chemistry.chemistry_gradio import chat
    agent_options, launch_options = split_options(kwargs)
    ui = chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
def literature(**kwargs):
    """Start the Literature Agent for working with scientific publications."""
    from aurelian.agents.literature.literature_gradio import chat
    agent_options, launch_options = split_options(kwargs)
    ui = chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
@click.argument("query", nargs=-1)
def monarch(query, **kwargs):
    """Start the Monarch Agent for biomedical knowledge exploration.
    
    The Monarch Agent provides access to relationships between genes, diseases, 
    phenotypes, and other biomedical entities through the Monarch Knowledge Base.
    
    If a query is provided, it will be run directly; otherwise, the chat interface will be launched.
    """
    from aurelian.agents.monarch.monarch_gradio import chat
    from aurelian.agents.monarch.monarch_agent import monarch_agent
    from aurelian.agents.monarch.monarch_config import get_config
    
    agent_options, launch_options = split_options(kwargs)
    
    if query:
        deps = get_config()
        if 'workdir' in agent_options and agent_options['workdir']:
            deps.workdir.location = agent_options['workdir']
        r = monarch_agent.run_sync(" ".join(query), deps=deps, **{k: v for k, v in agent_options.items() if k != 'workdir'})
        print(r.data)
    else:
        ui = chat(**agent_options)
        ui.launch(**launch_options)


@main.command()
@model_option
@workdir_option
@share_option
@server_port_option
@click.argument("query", nargs=-1)
def ubergraph(query, **kwargs):
    """Start the UberGraph Agent for SPARQL-based ontology queries.
    
    The UberGraph Agent provides a natural language interface to query ontologies 
    using SPARQL through the UberGraph endpoint. It helps users formulate and execute
    SPARQL queries without needing to know the full SPARQL syntax.
    
    If a query is provided, it will be run directly; otherwise, the chat interface will be launched.
    """
    from aurelian.agents.ubergraph.ubergraph_gradio import chat
    from aurelian.agents.ubergraph.ubergraph_agent import ubergraph_agent
    from aurelian.agents.ubergraph.ubergraph_config import get_config
    
    agent_options, launch_options = split_options(kwargs)
    
    if query:
        deps = get_config()
        if 'workdir' in agent_options and agent_options['workdir']:
            deps.workdir.location = agent_options['workdir']
        r = ubergraph_agent.run_sync(" ".join(query), deps=deps, **{k: v for k, v in agent_options.items() if k != 'workdir'})
        print(r.data)
    else:
        ui = chat(**agent_options)
        ui.launch(**launch_options)


# DO NOT REMOVE THIS LINE
# added this for mkdocstrings to work
# see https://github.com/bruce-szalwinski/mkdocs-typer/issues/18
#click_app = get_command(app)
#click_app.name = "aurelian"

if __name__ == "__main__":
    main()
