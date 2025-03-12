from dataclasses import dataclass, field
import os
from typing import List, Optional

from pydantic_ai import AgentRunError

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class LinkMLDependencies(HasWorkdir):
    """Configuration for the LinkML agent."""
    workdir: Optional[WorkDir] = None
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # Initialize workdir if not provided
        if self.workdir is None:
            self.workdir = WorkDir()

    def parse_objects_from_file(self, data_file: str) -> List[dict]:
        """
        Parse objects from a file in the working directory.

        Args:
            data_file: Name of the data file in the working directory

        Returns:
            List of parsed objects
        """
        from linkml_store.utils.format_utils import load_objects
        path_to_file = self.workdir.get_file_path(data_file)
        if not path_to_file.exists():
            raise AgentRunError(f"Data file {data_file} does not exist")
        return load_objects(path_to_file)


def get_config() -> LinkMLDependencies:
    """
    Get the LinkML agent configuration.
    
    Returns:
        LinkMLDependencies: The LinkML dependencies
    """
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return LinkMLDependencies(workdir=workdir)
