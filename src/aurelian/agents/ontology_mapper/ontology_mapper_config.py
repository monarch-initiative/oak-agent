"""
Configuration for the Ontology Mapper agent.
"""
from dataclasses import dataclass, field
import os
from typing import List, Optional

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class OntologyMapperDependencies(HasWorkdir):
    """
    Configuration for the ontology mapper agent.

    We include a default set of ontologies because the initial text embedding index is slow..
    this can easily be changed e.g. in command line
    """
    max_search_results: int = 30
    ontologies: List[str] = field(
        default_factory=lambda: ["mondo", "hp", "go", "uberon", "cl", "mp", "envo"]
    )
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()


def get_config(ontologies: Optional[List[str]] = None) -> OntologyMapperDependencies:
    """Get the Ontology Mapper configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    config = OntologyMapperDependencies(workdir=workdir)
    
    # Set ontologies if specified
    if ontologies:
        config.ontologies = ontologies
    
    # Allow environment variable to override max search results
    max_results_env = os.environ.get("MAX_SEARCH_RESULTS")
    if max_results_env:
        try:
            config.max_search_results = int(max_results_env)
        except ValueError:
            pass
    
    return config