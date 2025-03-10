"""
Configuration for the Ubergraph agent.
"""
from dataclasses import dataclass, field
import os
from typing import Dict, Optional

from aurelian.dependencies.workdir import HasWorkdir, WorkDir

# Default UberGraph endpoint
UBERGRAPH_ENDPOINT = "https://ubergraph.apps.renci.org/sparql"

# Default SPARQL prefixes
DEFAULT_PREFIXES = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "obo": "http://purl.obolibrary.org/obo/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "renci": "http://reasoner.renci.org/",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
    "BFO": "http://purl.obolibrary.org/obo/BFO_",
    "RO": "http://purl.obolibrary.org/obo/RO_",
    "GO": "http://purl.obolibrary.org/obo/GO_",
    "SO": "http://purl.obolibrary.org/obo/SO_",
    "CHEBI": "http://purl.obolibrary.org/obo/CHEBI_",
    "CL": "http://purl.obolibrary.org/obo/CL_",
    "UBERON": "http://purl.obolibrary.org/obo/UBERON_",
    "IAO": "http://purl.obolibrary.org/obo/IAO_",
    "OBI": "http://purl.obolibrary.org/obo/OBI_",
    "biolink": "https://w3id.org/biolink/vocab/",
    "bds": "http://www.bigdata.com/rdf/search#",
}


@dataclass
class Dependencies(HasWorkdir):
    """Configuration for the UberGraph agent."""
    
    # SPARQL endpoint
    endpoint: str = UBERGRAPH_ENDPOINT
    
    # Prefixes for SPARQL queries
    prefixes: Dict[str, str] = field(default_factory=lambda: DEFAULT_PREFIXES)
    
    # Maximum number of results to return
    max_results: int = 20
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()


def get_config(
    endpoint: Optional[str] = None, 
    prefixes: Optional[Dict[str, str]] = None,
    max_results: Optional[int] = None,
) -> Dependencies:
    """Get the UberGraph configuration from environment variables or defaults."""
    # Initialize from environment or defaults
    config_endpoint = endpoint or os.environ.get("UBERGRAPH_ENDPOINT", UBERGRAPH_ENDPOINT)
    config_max_results = max_results or int(os.environ.get("MAX_RESULTS", "20"))
    
    # Get workdir from environment if specified
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    # Create config with the specified values
    config = Dependencies(
        endpoint=config_endpoint,
        prefixes=prefixes or DEFAULT_PREFIXES,
        max_results=config_max_results,
        workdir=workdir,
    )
    
    return config