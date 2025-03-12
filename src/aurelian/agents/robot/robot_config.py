from dataclasses import field, dataclass
import os
from typing import Dict, Optional

from aurelian.dependencies.workdir import WorkDir, HasWorkdir


@dataclass
class RobotDependencies(HasWorkdir):
    """Configuration for the ROBOT ontology agent."""
    workdir: WorkDir = field(default_factory=lambda: WorkDir())
    prefix_map: Dict[str, str] = field(default_factory=lambda: {"ex": "http://example.org/"})


def get_config() -> RobotDependencies:
    """
    Get the ROBOT configuration from environment variables or defaults.
    
    Returns:
        RobotDependencies: The ROBOT dependencies
    """
    workdir_path = os.environ.get("ROBOT_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    return RobotDependencies(workdir=workdir)