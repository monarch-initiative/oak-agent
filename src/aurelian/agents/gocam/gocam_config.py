"""
Configuration classes for the GOCAM agent.
"""
from dataclasses import dataclass, field
from typing import Optional

from bioservices import UniProt
from linkml_store import Client
from linkml_store.api import Collection

from aurelian.dependencies.workdir import HasWorkdir

# Default database connection settings
HANDLE = "mongodb://localhost:27017/gocams"
DB_NAME = "gocams"
COLLECTION_NAME = "main"

# Initialize UniProt service
uniprot_service = UniProt(verbose=False)


@dataclass
class GOCAMDependencies(HasWorkdir):
    """
    Configuration for the GOCAM agent.
    """
    max_results: int = field(default=10)
    db_path: str = field(default=HANDLE)
    db_name: str = field(default=DB_NAME)
    collection_name: str = field(default=COLLECTION_NAME)
    _collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        """
        Get the GOCAM collection, initializing the connection if needed.
        
        Returns:
            Collection: The GOCAM collection
        """
        if self._collection is None:
            client = Client()
            client.attach_database(self.db_path, alias=self.db_name)
            db = client.databases[self.db_name]
            self._collection = db.get_collection(self.collection_name)
        return self._collection
    
    def get_uniprot_service(self) -> UniProt:
        """
        Get the UniProt service for protein lookups.
        
        Returns:
            UniProt: The UniProt service
        """
        return uniprot_service