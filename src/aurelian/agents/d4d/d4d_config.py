"""
Configuration for the D4D (Datasheets for Datasets) agent.
"""
from dataclasses import dataclass
import os

from aurelian.dependencies.workdir import HasWorkdir, WorkDir


@dataclass
class D4DConfig(HasWorkdir):
    """Configuration for the D4D agent."""
    
    schema_url: str = "https://raw.githubusercontent.com/monarch-initiative/ontogpt/main/src/ontogpt/templates/data_sheets_schema.yaml"
    
    def __post_init__(self):
        """Initialize the config with default values."""
        # HasWorkdir doesn't have a __post_init__ method, so we don't call super()
        if self.workdir is None:
            self.workdir = WorkDir()


def get_config(schema_url: str = None) -> D4DConfig:
    """
    Get the D4D configuration from environment variables or defaults.
    
    Args:
        schema_url: The URL to the schema YAML (overrides environment variable)
        
    Returns:
        A D4DConfig instance
    """
    # Try to get from environment, then use provided values or defaults
    env_schema_url = os.environ.get("AURELIAN_D4D_SCHEMA_URL", None)
    
    # Use provided values first, then environment, then defaults
    final_schema_url = schema_url or env_schema_url
    
    workdir_path = os.environ.get("AURELIAN_WORKDIR", None)
    workdir = WorkDir(location=workdir_path) if workdir_path else None
    
    config = D4DConfig(workdir=workdir)
    if final_schema_url:
        config.schema_url = final_schema_url
        
    return config