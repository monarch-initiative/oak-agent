import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.chemistry.chemistry_config import ChemistryDependencies as Dependencies
from aurelian.agents.chemistry.chemistry_agent import chemistry_agent


@pytest.fixture
def deps():
    return Dependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Look at the structure for CHEBI:144139 - what type of terpenoid is it?", "triterpenoid"),
    ],
)
def test_chemistry_agent(deps, query, ideal):
    r = chemistry_agent.run_sync(query, deps=deps)
    for m in r.all_messages():
        print(m)
    data = r.data
    assert data is not None
    if ideal is not None:
        if isinstance(ideal, list):
            for i in ideal:
                assert i in data
        else:
            assert ideal in data
