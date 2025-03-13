"""
Tests for CLI commands execution.

This file contains tests for CLI command execution, including direct query mode.
These tests mock out dependencies to avoid making actual API calls.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from aurelian.cli import main


@pytest.fixture
def mock_agent_runner():
    """Mock the agent Runner to avoid actual API calls."""
    with patch("aurelian.cli.run_agent") as mock_run:
        mock_run.return_value = None
        yield mock_run


def test_agent_ui_mode(mock_agent_runner):
    """Test running an agent in UI mode."""
    runner = CliRunner()
    result = runner.invoke(main, ["diagnosis", "--ui"])
    assert result.exit_code == 0
    mock_agent_runner.assert_called_once()
    args, kwargs = mock_agent_runner.call_args
    assert kwargs["ui"] is True
    assert kwargs["query"] == ()


def test_agent_direct_query_mode(mock_agent_runner):
    """Test running an agent in direct query mode."""
    runner = CliRunner()
    result = runner.invoke(main, ["diagnosis", "test query"])
    assert result.exit_code == 0
    mock_agent_runner.assert_called_once()
    args, kwargs = mock_agent_runner.call_args
    assert kwargs["ui"] is False
    # Click passes this as a tuple with one string containing the whole query
    assert kwargs["query"] == ("test query",)


def test_chemistry_command(mock_agent_runner):
    """Test the chemistry command specifically since we just fixed it."""
    runner = CliRunner()
    result = runner.invoke(main, ["chemistry", "what is aspirin"])
    assert result.exit_code == 0
    mock_agent_runner.assert_called_once()
    args, kwargs = mock_agent_runner.call_args
    # Check correct parameters are passed 
    assert "chemistry" == kwargs.get("agent_name", args[0])
    # Validate query format
    assert kwargs["query"] == ("what is aspirin",)


def test_datasheets_help():
    """Test the datasheets help, which has URL instead of QUERY."""
    runner = CliRunner()
    result = runner.invoke(main, ["datasheets", "--help"])
    assert result.exit_code == 0
    # Different wording for URL-based command
    assert "Run with a URL for direct mode" in result.output


def test_all_agent_commands_help():
    """Test that all agent commands display help correctly."""
    runner = CliRunner()
    commands = [
        "amigo", "biblio", "checklist", "chemistry", 
        "diagnosis", "gocam", "linkml", "literature", "mapper", 
        "monarch", "phenopackets", "rag", "robot", "ubergraph"
    ]
    
    for command in commands:
        result = runner.invoke(main, [command, "--help"])
        assert result.exit_code == 0, f"Help for {command} failed with {result.output}"
        assert "Run with a query for direct mode" in result.output or "Run with a URL for direct mode" in result.output, \
            f"Missing mode info in {command} help"