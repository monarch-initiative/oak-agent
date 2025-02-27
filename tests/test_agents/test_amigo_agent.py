import os
import pytest
from aurelian.agents.amigo_agent import gene_associations_for_pmid, AmiGODependencies, amigo_agent
from oaklib import get_adapter

pytestmark = pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skipping in GitHub Actions"
)

def test_pmid():
    """
    Test the PMID function
    """
    amigo = get_adapter(f"amigo:NCBITaxon:9606")
    pmid = "PMID:19661248"
    assocs = gene_associations_for_pmid(amigo, pmid)
    assert len(assocs) > 0
    assert len(assocs) < 20
    assert all(a for a in assocs if pmid in a["publications"])



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
