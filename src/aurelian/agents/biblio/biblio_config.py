"""
Configuration for the Biblio agent.
"""
from dataclasses import dataclass, field
from typing import Optional

from linkml_store import Client
from linkml_store.api import Collection

from aurelian.dependencies.workdir import HasWorkdir, WorkDir
from . import HANDLE, DB_NAME, COLLECTION_NAME


@dataclass
class BiblioDependencies(HasWorkdir):
    """Configuration for the Biblio agent."""
    
    max_results: int = field(default=10)
    _collection: Optional[Collection] = None
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()

    @property
    def collection(self) -> Collection:
        """Get the database collection, initializing it if needed."""
        if self._collection is None:
            client = Client()
            client.attach_database(HANDLE, alias=DB_NAME)
            db = client.databases[DB_NAME]
            self._collection = db.get_collection(COLLECTION_NAME)
        return self._collection


def get_config() -> BiblioDependencies:
    """Get the Biblio configuration with default settings."""
    return BiblioDependencies()