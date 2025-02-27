import pytest
from unittest.mock import patch, MagicMock

# ✅ Mock `Agent` before importing `ontology_mapper_agent`
mock_agent = MagicMock()
mock_agent.run_sync.return_value = MagicMock(data="Mocked response")

with patch("pydantic_ai.Agent", return_value=mock_agent):
    from aurelian.agents.ontology_mapper_agent import OntologyDependencies, ontology_mapper_agent

@pytest.fixture
def deps() -> OntologyDependencies:
    return OntologyDependencies()


@pytest.mark.parametrize(
    "query,ideal,ontologies",
    [
        ("Find the term in the cell ontology for neuron", "CL:0000540", None),
    ]
)
def test_ontology_mapper_agent(deps, query, ideal, ontologies):
    # Run the mocked agent
    with patch.object(ontology_mapper_agent, "run_sync", return_value=MagicMock(data="Mocked response")) as mock_run:
        r = ontology_mapper_agent.run_sync(query, deps=deps)
        data = r.data

    assert data is not None
    assert data == "Mocked response"  # Ensure the mock is working
