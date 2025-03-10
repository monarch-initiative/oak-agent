"""
Configuration classes for the literature agent.
"""
from dataclasses import dataclass
from typing import Optional

from aurelian.dependencies.workdir import HasWorkdir


@dataclass
class LiteratureDependencies(HasWorkdir):
    """
    Configuration for the literature agent.
    """
    max_results: int = 10