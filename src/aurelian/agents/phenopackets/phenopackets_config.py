"""
Configuration classes for the phenopackets agent.
"""
from dataclasses import dataclass, field
from typing import Optional

from linkml_store import Client
from linkml_store.api import Collection

from aurelian.dependencies.workdir import HasWorkdir

HANDLE = "mongodb://localhost:27017/phenopackets"
DB_NAME = "phenopackets"
COLLECTION_NAME = "main"


@dataclass
class PhenopacketsDependencies(HasWorkdir):
    """
    Configuration for the phenopackets agent.
    """
    max_results: int = field(default=10)
    db_path: str = field(default=HANDLE)
    db_name: str = field(default=DB_NAME)
    collection_name: str = field(default=COLLECTION_NAME)
    _collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        """
        Get the phenopackets collection, initializing the connection if needed.
        
        Returns:
            Collection: The phenopackets collection
        """
        if self._collection is None:
            client = Client()
            client.attach_database(self.db_path, alias=self.db_name)
            db = client.databases[self.db_name]
            self._collection = db.get_collection(self.collection_name)
        return self._collection