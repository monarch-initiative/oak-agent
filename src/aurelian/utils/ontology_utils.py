from oaklib import BasicOntologyInterface
from oaklib.datamodels.search import create_search_configuration
from oaklib.interfaces import SearchInterface


def search_ontology(adapter: BasicOntologyInterface, query: str, limit=10):
    """Search the ontology for the given query term.

    Example:
        >>> from oaklib import get_adapter
        >>> adapter = get_adapter("sqlite:obo:uberon")
        >>> terms = search_ontology(adapter, "manus")
        >>> assert len(terms) > 1
        >>> terms = search_ontology(adapter, "l~digit", limit=5)
        >>> assert len(terms) == 5

    :param adapter: The ontology adapter.
    :param query: The query term.
    :param limit: The maximum number of search results to return.
    :return: The search results.

    """
    if not isinstance(adapter, SearchInterface):
        raise ValueError(f"adapter must be an instance of SearchInterface, not {type(adapter)}")
    cfg = create_search_configuration(query)
    search_term = cfg.search_terms[0]
    objs = []
    for i, curie in enumerate(adapter.basic_search(search_term, config=cfg)):
        if i >= limit:
            break
        objs.append({"id": curie, "label": adapter.label(curie), "description": adapter.definition(curie)})

    return objs
