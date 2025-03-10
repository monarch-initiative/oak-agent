"""
Configuration for the RAG agent.
"""
from dataclasses import dataclass, field
import os
from typing import Optional

from linkml_store import Client
from linkml_store.api import Collection

from aurelian.dependencies.workdir import HasWorkdir, WorkDir
from . import COLLECTION_NAME


@dataclass
class RagDependencies(HasWorkdir):
    """Configuration for the RAG agent."""
    
    db_path: str
    collection_name: str = COLLECTION_NAME
    max_results: int = field(default=10)
    max_content_len: int = 5000
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
            db_path = self.db_path
            client.attach_database(db_path)
            db = client.databases[db_path]
            self._collection = db.get_collection(self.collection_name)
        return self._collection


def get_config(db_path: Optional[str] = None, collection_name: Optional[str] = None) -> RagDependencies:
    """
    Get the RAG configuration from environment variables or defaults.
    
    Args:
        db_path: The database path to use (overrides environment variable)
        collection_name: The collection name to use (overrides environment variable)
        
    Returns:
        A RagDependencies instance
    """
    # Try to get from environment, then use provided values or defaults
    env_db_path = os.environ.get("AURELIAN_RAG_DB_PATH", None)
    env_collection = os.environ.get("AURELIAN_RAG_COLLECTION", COLLECTION_NAME)
    
    # Use provided values first, then environment, then defaults
    final_db_path = db_path or env_db_path
    final_collection = collection_name or env_collection
    
    if not final_db_path:
        raise ValueError("Database path must be provided either as parameter or via AURELIAN_RAG_DB_PATH environment variable")
    
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return RagDependencies(
        db_path=final_db_path,
        collection_name=final_collection,
        workdir=workdir,
    )