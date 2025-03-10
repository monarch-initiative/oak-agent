"""
Tests for the UniProt agent.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from pydantic_ai import ModelRetry

from aurelian.agents.uniprot.uniprot_agent import uniprot_agent
from aurelian.agents.uniprot.uniprot_tools import (
    normalize_uniprot_id,
    search,
    lookup_uniprot_entry,
    uniprot_mapping,
)
from aurelian.agents.uniprot.uniprot_config import UniprotConfig, get_config
from aurelian.dependencies.workdir import WorkDir


def test_normalize_uniprot_id():
    """Test normalization of UniProt IDs."""
    # Test with version number
    assert normalize_uniprot_id("P12345.2") == "P12345.2"
    
    # Test with prefix
    assert normalize_uniprot_id("UniProtKB:P12345") == "P12345"
    
    # Test with no changes needed
    assert normalize_uniprot_id("P12345") == "P12345"


@pytest.fixture
def mock_uniprot_client():
    """Fixture to mock the UniProt client."""
    with patch("bioservices.UniProt") as mock_uniprot:
        mock_instance = MagicMock()
        mock_uniprot.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_config(mock_uniprot_client):
    """Fixture to create a mock config with the mocked client."""
    config = UniprotConfig()
    config.get_uniprot_client = MagicMock(return_value=mock_uniprot_client)
    return config


def test_search(mock_config, mock_uniprot_client):
    """Test the search function."""
    # Setup the mock to return a sample response
    mock_uniprot_client.search.return_value = "Entry\tGene\nP12345\tINS"
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function
    result = search(ctx, "insulin human")
    
    # Verify the result
    assert "P12345" in result
    assert "INS" in result
    
    # Verify the mock was called with expected arguments
    mock_uniprot_client.search.assert_called_once()
    args, kwargs = mock_uniprot_client.search.call_args
    assert args[0] == "insulin human"
    assert kwargs["frmt"] == "tsv"


def test_search_empty_results(mock_config, mock_uniprot_client):
    """Test the search function with empty results."""
    # Setup the mock to return an empty response
    mock_uniprot_client.search.return_value = ""
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function and expect an exception
    with pytest.raises(ModelRetry) as excinfo:
        search(ctx, "nonexistent protein")
    
    # Verify the exception message
    assert "No results found for query" in str(excinfo.value)


def test_lookup_uniprot_entry(mock_config, mock_uniprot_client):
    """Test the lookup_uniprot_entry function."""
    # Setup the mock to return a sample response
    mock_uniprot_client.retrieve.return_value = "ID   INS_HUMAN              Reviewed;"
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function
    result = lookup_uniprot_entry(ctx, "P01308")
    
    # Verify the result
    assert "INS_HUMAN" in result
    
    # Verify the mock was called with expected arguments
    mock_uniprot_client.retrieve.assert_called_once_with("P01308", frmt="txt")


def test_lookup_uniprot_entry_empty_result(mock_config, mock_uniprot_client):
    """Test the lookup_uniprot_entry function with empty results."""
    # Setup the mock to return an empty response
    mock_uniprot_client.retrieve.return_value = ""
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function and expect an exception
    with pytest.raises(ModelRetry) as excinfo:
        lookup_uniprot_entry(ctx, "INVALID")
    
    # Verify the exception message
    assert "No entry found for accession" in str(excinfo.value)


def test_uniprot_mapping(mock_config, mock_uniprot_client):
    """Test the uniprot_mapping function."""
    # Setup the mock to return a sample response
    mock_uniprot_client.mapping.return_value = {"P01308": ["1MSO", "1ZNJ"]}
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function
    result = uniprot_mapping(ctx, "PDB", ["P01308", "P01009"])
    
    # Verify the result
    assert "P01308" in result
    assert "1MSO" in result["P01308"]
    
    # Verify the mock was called with expected arguments
    mock_uniprot_client.mapping.assert_called_once()
    args, kwargs = mock_uniprot_client.mapping.call_args
    assert args[0] == "UniProtKB_AC-ID"
    assert args[1] == "PDB"
    assert "P01308" in args[2]
    assert "P01009" in args[2]


def test_uniprot_mapping_empty_input(mock_config, mock_uniprot_client):
    """Test the uniprot_mapping function with empty input."""
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function and expect an exception
    with pytest.raises(ModelRetry) as excinfo:
        uniprot_mapping(ctx, "PDB", [])
    
    # Verify the exception message
    assert "No UniProt accessions provided" in str(excinfo.value)


def test_uniprot_mapping_empty_result(mock_config, mock_uniprot_client):
    """Test the uniprot_mapping function with empty results."""
    # Setup the mock to return an empty response
    mock_uniprot_client.mapping.return_value = {}
    
    # Create a mock context with our config
    ctx = MagicMock()
    ctx.deps = mock_config
    
    # Call the function and expect an exception
    with pytest.raises(ModelRetry) as excinfo:
        uniprot_mapping(ctx, "INVALID_DB", ["P01308"])
    
    # Verify the exception message
    assert "No mappings found" in str(excinfo.value)


# ===== Integration tests with the actual UniProt agent =====

# Skip integration tests in CI environments
if os.getenv("GITHUB_ACTIONS") == "true":
    pytestmark = pytest.mark.skip(reason="Skipping integration tests in GitHub Actions")
else:
    # Mark as integration tests that might be flaky due to external API calls
    pytestmark = [
        pytest.mark.integration,
        pytest.mark.flaky(reruns=1, reruns_delay=2),
    ]


@pytest.fixture
def deps():
    """Fixture to create a real UniProt dependencies object for integration tests."""
    config = get_config()
    config.workdir = WorkDir.create_temporary_workdir()
    return config


@pytest.mark.parametrize(
    "query,ideal",
    [
        (
            "Look up information about UniProt entry P01308", 
            ["insulin", "human", "diabetes"]
        ),
        (
            "Map UniProt ID P01308 to PDB database", 
            ["pdb", "entries", "1a7f"]
        ),
    ],
)
def test_uniprot_agent_integration(record_property, deps, query, ideal):
    """Integration test for the UniProt agent with real API calls."""
    # Record test metadata for reporting
    record_property("agent", str(uniprot_agent))
    record_property("query", query)

    # Call the agent
    r = uniprot_agent.run_sync(query, deps=deps)
    data = r.data
    
    # Record the result
    record_property("result", str(data))
    
    # Verify results
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, (list, tuple)):
            for i in ideal:
                assert i.lower() in data.lower()
        else:
            assert ideal.lower() in data.lower()