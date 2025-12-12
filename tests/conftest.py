import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib.server import app

# --- Mock Data Fixture ---
@pytest.fixture
def mock_inventory_data():
    """Mock inventory data for testing."""
    return [
        {"id": 1, "name": "Bread", "price": 5, "stock": 10},
        {"id": 2, "name": "Peanut Butter", "price": 3, "stock": 5},
    ]

@pytest.fixture
def client(mock_inventory_data):
    """Creates a Flask test client with mocked utilities."""

    # We patch utility functions (load/save) to use mock data instead of files
    with patch('lib.server.load_data', return_value=mock_inventory_data), \
         patch('lib.server.save_data'):

        # Configure app for testing
        app.config['TESTING'] = True

        # Yield the test client
        with app.test_client() as client:
            yield client