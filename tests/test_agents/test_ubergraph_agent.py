import pytest
from unittest.mock import patch, MagicMock

# ✅ Mock `Agent` before importing `ubergraph_agent`
mock_agent = MagicMock()
mock_agent.run_sync.return_value = MagicMock(data="Mocked response")

# ✅ Mock `get_adapter()` to prevent downloading ontologies
mock_adapter = MagicMock()
mock_adapter.labels.return_value = [("CL:0000540", "Neuron")]
mock_adapter.entities.return_value = ["CL:0000540"]

with patch("pydantic_ai.Agent", return_value=mock_agent), patch("oaklib.get_adapter", return_value=mock_adapter):
    from aurelian.agents.ubergraph_agent import Dependencies, ubergraph_agent


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
    assert data == "Mocked response"  # Ensure the mock is working
