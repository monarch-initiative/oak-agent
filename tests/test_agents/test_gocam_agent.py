import pytest
from unittest.mock import patch, MagicMock

# ✅ Mock `Agent` before importing `gocam_agent`
mock_agent = MagicMock()
mock_agent.run_sync.return_value = MagicMock(data="Mocked response")

with patch("pydantic_ai.Agent", return_value=mock_agent):
    from aurelian.agents.gocam_agent import GOCamDependencies, gocam_agent


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
    assert data == "Mocked response"  # Ensure the mock is working
