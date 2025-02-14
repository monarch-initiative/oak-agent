import pytest

from oak_agent.agents.gocam_agent import GOCamDependencies, gocam_agent


def test_gocam_agent():
    deps = GOCamDependencies()
    r = gocam_agent.run_sync("Find a model relating to apoptosis and list their genes", deps=deps)
    print(f"Result: {r}")
    data = r.data
    assert data is not None
    print(data)
    assert "CASP" in data

def test_bad_id():
    deps = GOCamDependencies()
    r = gocam_agent.run_sync("Find a model with ID gomodel:123", deps=deps)
    print(f"Result: {r}")
