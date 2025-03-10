"""
Tests for the Monarch agent.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
import asyncio

from pydantic_ai import ModelRetry

from aurelian.agents.monarch.monarch_agent import monarch_agent
from aurelian.agents.monarch.monarch_tools import (
    get_gene_id,
    get_disease_id,
)
from aurelian.agents.monarch.monarch_config import MonarchDependencies, get_config


def test_get_gene_id():
    """Test gene ID normalization."""
    ctx = MagicMock()
    assert get_gene_id(ctx, "BRCA1") == "BRCA1"
    assert get_gene_id(ctx, "Gene:BRCA1") == "Gene:BRCA1"


def test_get_disease_id():
    """Test disease ID normalization."""
    ctx = MagicMock()
    assert get_disease_id(ctx, "MONDO:0007254") == "MONDO:0007254"
    assert get_disease_id(ctx, "OMIM:143100") == "OMIM:143100"


# ===== Integration tests with the actual Monarch agent =====

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
    """Fixture to create a real Monarch dependencies object for integration tests."""
    return get_config()


@pytest.mark.parametrize(
    "query,ideal",
    [
        (
            "Find associations for gene BRCA1", 
            ["BRCA1", "gene"]
        ),
        (
            "What diseases are associated with MONDO:0007254?", 
            ["disease", "association"]
        ),
    ],
)
def test_monarch_agent_integration(record_property, deps, query, ideal):
    """Integration test for the Monarch agent with real API calls."""
    # Record test metadata for reporting
    record_property("agent", str(monarch_agent))
    record_property("query", query)
    
    # Call the agent
    r = monarch_agent.run_sync(query, deps=deps)
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