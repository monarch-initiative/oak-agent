import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.phenopackets.phenopackets_config import PhenopacketsDependencies
from aurelian.agents.phenopackets.phenopackets_agent import phenopackets_agent


@pytest.fixture
def deps():
    return PhenopacketsDependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("What phenotypes are associated with peroxisomal disorders?", "peroxisomal"),
        ("Find patients with liver disease", "liver"),
        ("What are the most common genes involved in skeletal dysplasias?", "skeletal"),
    ],
)
def test_phenopackets_agent(deps, query, ideal):
    r = phenopackets_agent.run_sync(query, deps=deps)
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