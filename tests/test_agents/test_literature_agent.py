import pytest
import os

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("Skipping in GitHub Actions", allow_module_level=True)

from aurelian.agents.literature.literature_config import LiteratureDependencies
from aurelian.agents.literature.literature_agent import literature_agent


@pytest.fixture
def deps():
    return LiteratureDependencies()


@pytest.mark.parametrize(
    "query,ideal",
    [
        ("What is the abstract of PMID:31653696?", "Loss-of-function mutations in the gene encoding human protein DJ-1 cause early onset of Parkinson's disease"),
        ("Tell me about the gene DJ-1 and Parkinson's disease", "Parkinson"),
        ("What does the literature say about circadian rhythm and sleep disorders?", "circadian"),
    ],
)
def test_literature_agent(deps, query, ideal):
    r = literature_agent.run_sync(query, deps=deps)
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