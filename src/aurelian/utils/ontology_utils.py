import logfire
import pystow
from cachetools.func import lru_cache
from linkml_store.api import Collection
from linkml_store.api.stores.duckdb import DuckDBDatabase
from linkml_store.index import LLMIndexer
from oaklib import BasicOntologyInterface, get_adapter

llm_indexer = LLMIndexer()


@lru_cache
def get_collection_for_adapter(handle: str, name: str) -> Collection:
    """
    Retrieve or create a cached ontology collection.

    Args:
        handle (str): The ontology handle (e.g., `sqlite:obo:uberon`).
        name (str): The name of the ontology (e.g., `uberon`).

    Returns:
        Collection: The indexed ontology collection.
    """
    adapter = get_adapter(handle)
    cache_dir = pystow.join("aurelian", "indexes")
    duckdb_path = str(cache_dir / f"{name}.duckdb")
    database = DuckDBDatabase(duckdb_path)
    collection = database.get_collection(name, create_if_not_exists=True)

    if collection.size() > 0:
        return collection

    objs = [{"id": id, "label": lbl} for id, lbl in adapter.labels(adapter.entities())]
    collection.insert(objs)
    return collection


def search_ontology(adapter: BasicOntologyInterface, query: str, limit=10):
    """
    Search the ontology for the given query term.

    Example:
        >>> from oaklib import get_adapter
        >>> adapter = get_adapter("sqlite:obo:uberon")
        >>> terms = search_ontology(adapter, "manus")
        >>> assert len(terms) > 1
        >>> terms = search_ontology(adapter, "l~digit", limit=5)
        >>> assert len(terms) == 5

    Args:
        adapter (BasicOntologyInterface): The ontology adapter.
        query (str): The query term.
        limit (int): The maximum number of search results to return.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing ontology term IDs and labels.
    """
    scheme = adapter.resource.scheme
    name = adapter.resource.slug
    local_name = name.split(":")[-1]
    handle = f"{scheme}:{name}"

    collection = get_collection_for_adapter(handle, local_name)
    with logfire.span("search_ontology {name} {query}", name=name, query=query):
        logfire.info(f"Searching {scheme}:{name} for {query}")
        qr = collection.search(query, limit=limit, index_name="llm")
        objs = [(obj["id"], obj["label"]) for obj in qr.rows]
    return objs
