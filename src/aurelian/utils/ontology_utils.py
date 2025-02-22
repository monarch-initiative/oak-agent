import pystow
from cachetools.func import lru_cache
from linkml_store.api import Collection
from linkml_store.api.stores.duckdb import DuckDBDatabase
from linkml_store.index import LLMIndexer
from oaklib import BasicOntologyInterface, get_adapter
from oaklib.datamodels.search import create_search_configuration
from oaklib.implementations import SqlImplementation
from oaklib.interfaces import OboGraphInterface, SearchInterface
from sqlalchemy import text

llm_indexer = LLMIndexer()



@lru_cache
def get_collection_for_adapter(handle: str, name: str) -> Collection:
    adapter = get_adapter(handle)
    cache_dir = pystow.join('aurelian', 'indexes')
    duckdb_path = str(cache_dir / f"{name}.duckdb")
    database = DuckDBDatabase(duckdb_path)
    collection = database.get_collection(name, create_if_not_exists=True)
    if collection.size() > 0:
        return collection
    objs = []
    for id, lbl in adapter.labels(adapter.entities()):
        objs.append({"id": id, "label": lbl})
    collection.insert(objs)
    return collection


def search_ontology(adapter: BasicOntologyInterface, query: str, limit=10):
    """
    Search the ontology for the given query term.

    Example:

        >>> from oaklib import get_adapter
        >>> adapter = get_adapter("sqlite:obo:bfo")
        >>> objs = search_ontology(adapter, "3D spatial")
        >>> for id, label in objs:
        ...     print(id, label)
        BFO:0000028 three-dimensional spatial region
        ...

    """
    scheme = adapter.resource.scheme
    name = adapter.resource.slug
    local_name = name.split(":")[-1]
    handle = f"{scheme}:{name}"
    collection = get_collection_for_adapter(handle, local_name)
    qr = collection.search(query, limit=limit, index_name="llm")
    objs = [(obj["id"], obj["label"]) for obj in qr.rows]
    return objs
