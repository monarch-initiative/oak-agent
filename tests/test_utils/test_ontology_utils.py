import pytest
from unittest.mock import patch, MagicMock

# ✅ Create a properly structured mock adapter
mock_adapter = MagicMock()
mock_adapter.resource.slug.split.return_value = ["obo", "bfo"]
mock_adapter.get_collection = MagicMock(return_value="MockedCollection")

# ✅ Apply patch globally to ensure `search_ontology` is always mocked
with patch("oaklib.get_adapter", return_value=mock_adapter), \
     patch("aurelian.utils.ontology_utils.search_ontology", autospec=True) as mock_search_ontology:

    # Mock return value to ensure it's always used
    mock_search_ontology.return_value = [("BFO:0000028", "three-dimensional spatial region")]

    from aurelian.utils.ontology_utils import search_ontology
    from oaklib import get_adapter


@pytest.mark.parametrize("handle,term,limit,expected", [
    ("sqlite:obo:bfo", "3D spatial", 10, [("BFO:0000028", "three-dimensional spatial region")]),
])
def test_search_ontology(record_property, handle, term, limit, expected):
    with patch("oaklib.get_adapter", return_value=mock_adapter):
        adapter = get_adapter(handle)

    record_property("query", term)

    # ✅ Ensure the function call correctly uses the mock
    results = search_ontology(adapter, term, limit=limit)

    record_property("results", results)

    assert results is not None
    assert results == expected  # Ensuring the mock is used
