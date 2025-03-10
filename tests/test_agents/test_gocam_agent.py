import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.gocam.gocam_config import GOCAMDependencies
from aurelian.agents.gocam.gocam_agent import gocam_agent


@pytest.fixture
def deps():
    return GOCamDependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("Find a model relating to apoptosis and list their genes", "CASP"),
        ("How many distinct gene products in 62b4ffe300001804? Answer with a number, e.g. 7.", "4"),
        ("Find a model with ID gomodel:1234 and summarize it", None),
    ],
)
def test_gocam_agent(deps, query, ideal):
    r = gocam_agent.run_sync(query, deps=deps)
    data = r.data
    assert data is not None
    if ideal is not None:
        assert ideal in data
