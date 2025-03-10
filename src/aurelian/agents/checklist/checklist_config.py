"""
Configuration for the Checklist agent.
"""
from dataclasses import dataclass
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class ChecklistDependencies(HasWorkdir):
    """Configuration for the Checklist agent."""
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()


def get_config() -> ChecklistDependencies:
    """Get the Checklist configuration from environment variables or defaults."""
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return ChecklistDependencies(
        workdir=workdir,
    )