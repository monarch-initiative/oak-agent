"""
Configuration for the Diagnosis agent.
"""
from dataclasses import dataclass
import os
from typing import Optional

from oaklib.implementations import MonarchImplementation
from aurelian.dependencies.workdir import HasWorkdir, WorkDir

# Constants
HAS_PHENOTYPE = "biolink:has_phenotype"


@dataclass
class DiagnosisDependencies(HasWorkdir):
    """Configuration for the Diagnosis agent."""
    
    # Maximum number of search results to return
    max_search_results: int = 10
    
    # Monarch adapter
    monarch_adapter: Optional[MonarchImplementation] = None
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()
            
        # Initialize Monarch adapter if not provided
        if self.monarch_adapter is None:
            self.monarch_adapter = MonarchImplementation()


def get_config() -> DiagnosisDependencies:
    """Get the Diagnosis configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    # Get max search results from environment if available
    max_results_env = os.environ.get("MAX_SEARCH_RESULTS")
    max_results = int(max_results_env) if max_results_env and max_results_env.isdigit() else 10
    
    return DiagnosisDependencies(
        workdir=workdir,
        max_search_results=max_results,
    )