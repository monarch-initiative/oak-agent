import os

import pytest

from aurelian.agents.ubergraph_agent import Dependencies, ubergraph_agent

pytestmark = pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skipping in GitHub Actions"
)
@pytest.fixture
def deps():
    return Dependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Find the ID in the cell ontology of the term for 'neuron'", "CL:0000540"),
        ("Make a table with IDs of terms neuron, lymphocyte, and epithelial cell", ["CL:0000540"]),
    ],
)
def test_ubergraph_agent(deps, query, ideal):
    r = ubergraph_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, list):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data
