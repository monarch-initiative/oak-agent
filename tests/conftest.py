from pathlib import Path

from dotenv import load_dotenv
import pytest



@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables from .env file for all tests."""
    load_dotenv()
