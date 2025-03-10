"""
Configuration for the Monarch agent.
"""
from dataclasses import dataclass, field
import os
from typing import Dict, List, Optional

from oaklib import get_adapter
from oaklib.interfaces import OboGraphInterface

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class MonarchDependencies(HasWorkdir):
    """Configuration for the Monarch agent."""
    
    # Default taxon ID for humans
    taxon: str = "9606"
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()
            
    def get_monarch_adapter(self) -> OboGraphInterface:
        """Get a configured Monarch adapter."""
        return get_adapter("monarch:")
        
    def get_mondo_adapter(self) -> OboGraphInterface:
        """Get a configured Mondo adapter."""
        return get_adapter("sqlite:obo:mondo")


def get_config() -> MonarchDependencies:
    """Get the Monarch configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    taxon = os.environ.get("MONARCH_TAXON", "9606")
    
    return MonarchDependencies(
        workdir=workdir,
        taxon=taxon
    )