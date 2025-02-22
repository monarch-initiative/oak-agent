"""Command line interface for ubergraph-agent."""

import logging
from typing import Optional

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
share_option = click.option(
    "--share/--no-share",
    default=False,
    show_default=True,
    help="Share the agent GradIO chat via URL.",
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


def split_options(kwargs, agent_keys=["model"]):
    """Split options into model and agent options."""
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
def aria(share: bool, server_port: Optional[int] = None, **kwargs):
    """Start the Checklist UI."""
    import aurelian.agents.checklist_agent as aria

    ui = aria.chat(**kwargs)
    ui.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    main()
