"""Command line interface for ubergraph-agent."""

import logging
from typing import Optional, List

import click

from aurelian import __version__

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)

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
    help="Comma-separated list of ontologies to use for the agent.",
)
server_port_option = click.option(
    "--server-port",
    "-p",
    default=7860,
    show_default=True,
    help="The port to run the gradio server on.",
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """CLI for ubergraph-agent.

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
    """Split options into model and agent options."""
    if agent_keys is None:
        agent_keys = ["model", "workdir", "ontologies"]
    if extra_agent_keys is not None:
        agent_keys += extra_agent_keys
    agent_options = {k: v for k, v in kwargs.items() if k in agent_keys}
    launch_options = {k: v for k, v in kwargs.items() if k not in agent_keys}
    return agent_options, launch_options


@main.command()
def gocam_ui():
    """Start the GO-CAM UI."""
    import aurelian.agents.gocam_agent as gocam

    ui = gocam.ui()
    ui.launch()


@main.command()
@click.option("--limit", "-l", default=10, show_default=True, help="Number of results to return.")
@click.argument("ontology")
@click.argument("term")
def search_ontology(ontology: str, term: str, **kwargs):
    """Search the ontology for the given query term.

    Also has side effect of indexing
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
    """Start the GO-CAM UI."""
    import aurelian.agents.gocam_agent as gocam

    ui = gocam.chat(**kwargs)
    ui.launch(share=share, server_port=server_port)


@main.command()
@model_option
@share_option
@server_port_option
def phenopackets(**kwargs):
    """Start the GO-CAM UI."""
    import aurelian.agents.phenopacket_agent as phenopackets

    agent_options, launch_options = split_options(kwargs)
    ui = phenopackets.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
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
    import aurelian.agents.linkml_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
    ui.launch(**launch_options)


@main.command()
@model_option
@share_option
@server_port_option
def amigo(**kwargs):
    """Start the AmiGO agent."""
    import aurelian.agents.amigo_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
    ui.launch(**launch_options)

@main.command()
@model_option
@share_option
@server_port_option
@ontologies_option
def mapper(**kwargs):
    """Start the Ontology Mapper agent."""
    import aurelian.agents.ontology_mapper_agent as agent
    agent_options, launch_options = split_options(kwargs)
    ui = agent.chat(**agent_options)
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


if __name__ == "__main__":
    main()
