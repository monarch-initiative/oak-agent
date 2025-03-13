"""
Configuration classes for the literature agent.
"""
from dataclasses import dataclass
import os
from typing import Optional

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class LiteratureDependencies(HasWorkdir):
    """
    Configuration for the literature agent.
    """
    max_results: int = 10
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # Initialize workdir if not provided
        if self.workdir is None:
            self.workdir = WorkDir()


def get_config() -> LiteratureDependencies:
    """
    Get the Literature agent configuration from environment variables or defaults.
    
    Returns:
        LiteratureDependencies: The literature dependencies
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return LiteratureDependencies(workdir=workdir)