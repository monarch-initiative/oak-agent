import pytest

from aurelian.agents.ubergraph_agent import ubergraph_agent, Dependencies

@pytest.fixture
def model_name():
    return "openai:gpt-4o"

def test_ubergraph_agent(model_name):
    deps = Dependencies()
    r = ubergraph_agent.run_sync(
        "Find the ID in the cell ontology of the term for 'neuron'",
        deps=deps,
        model=model_name,
    )
    print(f"Result: {r}")
    data = r.data
    assert data is not None
    assert "CL:0000540" in data
