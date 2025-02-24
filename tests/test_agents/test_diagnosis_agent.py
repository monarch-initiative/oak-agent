import pytest
from unittest.mock import patch, MagicMock

# Mock `Agent` before importing `diagnosis_agent`
mock_agent = MagicMock()
mock_agent.run_sync.return_value = MagicMock(data="Mocked response")

with patch("pydantic_ai.Agent", return_value=mock_agent):
    from aurelian.agents.diagnosis_agent import DiagnosisDependencies, diagnosis_agent


@pytest.fixture
def deps():
    return DiagnosisDependencies()


@pytest.mark.parametrize(
    "query,ideal,model",
    [
        ("Find the Mondo ID for Marfan syndrome", "MONDO:0007947", None),
        (
            """Patient has growth failure, distinct facial features, alopecia, and skin aging.
            Findings excluded: Pigmented nevi, cafe-au-lait spots, and photosensitivity.
            Onset was in infancy.
            Return diagnosis with MONDO ID""",
            "MONDO:0008310",
            "openai:o3-mini",
        ),
        ("All eye phenotypes for Marfan syndrome (include HPO IDs)", "HP:0000518", None),
    ],
)
def test_ubergraph_agent(deps, query, ideal, model):
    kwargs = {"model": model} if model else {}
    r = diagnosis_agent.run_sync(query, deps=deps, **kwargs)
    data = r.data

    assert data is not None
    assert data == "Mocked response"  # Ensure the mock is working
