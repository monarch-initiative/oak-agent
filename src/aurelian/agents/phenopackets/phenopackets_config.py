"""
Configuration classes for the phenopackets agent.
"""
from dataclasses import dataclass, field
import os
from typing import Optional

from linkml_store import Client
from linkml_store.api import Collection

from aurelian.dependencies.workdir import HasWorkdir, WorkDir

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

    def __post_init__(self):
        """Initialize the config with default values."""
        # Initialize workdir if not provided
        if self.workdir is None:
            self.workdir = WorkDir()

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


def get_config() -> PhenopacketsDependencies:
    """
    Get the Phenopackets configuration from environment variables or defaults.
    
    Returns:
        PhenopacketsDependencies: The phenopackets dependencies
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    # Get any environment-specific settings
    db_path = os.environ.get("PHENOPACKETS_DB_PATH", HANDLE)
    db_name = os.environ.get("PHENOPACKETS_DB_NAME", DB_NAME)
    collection_name = os.environ.get("PHENOPACKETS_COLLECTION", COLLECTION_NAME)
    
    return PhenopacketsDependencies(
        workdir=workdir,
        db_path=db_path,
        db_name=db_name,
        collection_name=collection_name
    )