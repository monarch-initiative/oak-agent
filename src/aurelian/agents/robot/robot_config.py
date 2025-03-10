from dataclasses import field, dataclass
from typing import Dict

from aurelian.dependencies.workdir import WorkDir, HasWorkdir


@dataclass
class RobotDependencies(HasWorkdir):
    workdir: WorkDir = field(default_factory=lambda: WorkDir())
    prefix_map: Dict[str, str] = field(default_factory=lambda: {"ex": "http://example.org/"})