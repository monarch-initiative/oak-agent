"""
Tests for agent configurations required by the CLI.

This file contains tests to ensure all agents have the necessary configuration
functions required by the CLI, including the get_config function.
"""

import importlib
import os
import pytest
from pathlib import Path

# Set testing mode for agents that need special handling in tests
os.environ["TESTING"] = "1"


def get_agent_dirs():
    """Get all agent directories."""
    src_dir = Path(__file__).parent.parent / "src" / "aurelian" / "agents"
    agent_dirs = []
    
    for item in src_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            # Skip utility directories that aren't actual agents
            if item.name not in ["filesystem", "oak", "web"]:
                agent_dirs.append(item.name)
    
    return agent_dirs


def test_agent_dirs_exist():
    """Verify we're finding agent directories correctly."""
    agent_dirs = get_agent_dirs()
    # Ensure we find at least the known agents
    essential_agents = ["diagnosis", "amigo", "chemistry", "linkml"]
    for agent in essential_agents:
        assert agent in agent_dirs, f"Could not find essential agent: {agent}"


@pytest.mark.parametrize("agent_name", get_agent_dirs())
def test_agent_has_config_module(agent_name):
    """Test that each agent has a config module."""
    try:
        config_module = importlib.import_module(f"aurelian.agents.{agent_name}.{agent_name}_config")
        assert config_module is not None, f"Failed to import config module for {agent_name}"
    except ImportError as e:
        pytest.fail(f"Agent {agent_name} is missing a config module: {e}")


@pytest.mark.parametrize("agent_name", get_agent_dirs())
def test_agent_has_get_config_function(agent_name):
    """Test that each agent's config module has a get_config function."""
    try:
        config_module = importlib.import_module(f"aurelian.agents.{agent_name}.{agent_name}_config")
        assert hasattr(config_module, "get_config"), f"Agent {agent_name} config module missing get_config function"
        
        # Test that get_config is callable and returns something
        config = config_module.get_config()
        assert config is not None, f"get_config for {agent_name} returned None"
    except ImportError as e:
        pytest.fail(f"Failed to import config module for {agent_name}: {e}")
    except Exception as e:
        pytest.fail(f"Error calling get_config for {agent_name}: {e}")


@pytest.mark.parametrize("agent_name", get_agent_dirs())
def test_agent_config_has_workdir(agent_name):
    """Test that each agent's config has a workdir attribute."""
    try:
        config_module = importlib.import_module(f"aurelian.agents.{agent_name}.{agent_name}_config")
        config = config_module.get_config()
        
        # Test that config has workdir attribute
        assert hasattr(config, "workdir"), f"Agent {agent_name} config missing workdir attribute"
    except ImportError as e:
        pytest.fail(f"Failed to import config module for {agent_name}: {e}")
    except Exception as e:
        pytest.fail(f"Error getting workdir for {agent_name}: {e}")