"""
Tests for CLI command imports.

This test ensures that all CLI commands can be properly imported without errors.
"""
import importlib
import pytest
from click.testing import CliRunner

from aurelian.cli import main


def test_cli_main_help():
    """Test that the main CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def get_agent_commands():
    """Get all agent commands from the CLI."""
    # This gets all commands except for utility commands like search_ontology
    agent_commands = []
    for command in main.commands.values():
        if command.name not in ["search-ontology", "fulltext", "websearch", "geturl", "gocam-ui"]:
            agent_commands.append(command.name)
    return agent_commands


@pytest.mark.parametrize("command", get_agent_commands())
def test_agent_command_imports(command):
    """Test that importing each agent's modules works without errors."""
    runner = CliRunner()
    result = runner.invoke(main, [command, "--help"])
    assert result.exit_code == 0, f"Failed to import modules for command '{command}': {result.output}"
    assert f"Usage: " in result.output


def test_agent_direct_query_mode():
    """Test that agents can run in direct query mode."""
    # We'll use the diagnosis agent as an example since it's simple
    runner = CliRunner()
    result = runner.invoke(main, ["diagnosis", "--help"])
    assert result.exit_code == 0
    assert "Run with a query for direct mode" in result.output