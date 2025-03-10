import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.amigo.amigo_config import AmiGODependencies
from aurelian.agents.amigo.amigo_agent import amigo_agent
from oaklib import get_adapter


def test_pmid():
    """
    Test the PMID function
    """
    # This test now requires using the async function, so we'll skip it and move the logic to a test
    # that uses the agent directly
    pytest.skip("This test needs to be updated for the new async API structure.")



@pytest.fixture
def deps():
    return AmiGODependencies()

@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Lookup in amigo annotations to PMID:19661248 - what genes?", "Nox1"),
    ]
)
def test_amigo_agent(record_property, deps, query, ideal):
    record_property("agent", str(amigo_agent))
    record_property("query", query)
    r = amigo_agent.run_sync(query, deps=deps)
    data = r.data
    record_property("result", str(data))
    assert data is not None
    if ideal is not None:
        assert ideal in data
