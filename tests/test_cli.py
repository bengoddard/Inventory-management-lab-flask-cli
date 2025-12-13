import pytest
import subprocess
import sys
import json
import requests_mock
from unittest.mock import patch, MagicMock
from main import main
from io import StringIO
import requests

# Base command to run the CLI script
CLI_BASE_COMMAND = [sys.executable, "-m", "main"]
BASE_URL = "http://127.0.0.1:5000/inventory"

def run_cli_command(command_list, check=True):
    """Helper to execute a command and capture output."""
    full_command = CLI_BASE_COMMAND + command_list
    # Note: All arguments must be strings!
    return subprocess.run(
        [str(c) for c in full_command],
        capture_output=True,
        text=True,
        check=check # Raises CalledProcessError on non-zero exit code
    )

# --- Fixture for Mocking the External API Server ---
@pytest.fixture
def mock_api_server():
    """Provides a requests_mock context for simulating the server."""
    with requests_mock.Mocker() as m:
        # Mocking the common endpoints
        m.get(BASE_URL, json=[
            {"id": 1, "name": "Apple", "price": 1.5, "stock": 100}
        ], status_code=200)
        m.get(f"{BASE_URL}/1", json={"id": 1, "name": "Apple", "price": 1.5, "stock": 100}, status_code=200)
        m.get(f"{BASE_URL}/99", json={"error": "Not Found"}, status_code=404)

        # Mock successful POST response
        m.post(BASE_URL, json={"id": 3, "name": "Test", "price": 10, "stock": 100}, status_code=201)

        # Mock successful DELETE response
        m.delete(f"{BASE_URL}/5", text='', status_code=204)
        m.delete(f"{BASE_URL}/99", json={"error": "Not Found"}, status_code=404)

        yield m

@pytest.fixture
def mock_requests_post(mock_api_server):
    """Mocks requests.post used by your CLI functions."""
    with patch('requests.post') as mock:
        # Configure the mock to return a successful 201 response object
        mock_response = MagicMock()
        mock_response.status_code = 201
        # The .json() method should return the expected data
        mock_response.json.return_value = {"id": 3, "name": "TestItem", "price": 10, "stock": 100}
        mock_response.raise_for_status.return_value = None # Assume success
        mock.return_value = mock_response
        yield mock

@pytest.fixture
def mock_requests_get(mock_api_server):
    """Mocks requests.get used by your CLI functions."""
    with patch('requests.get') as mock:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Apple", "price": 1.5, "stock": 100},
            {"id": 2, "name": "Banana", "price": 0.5, "stock": 200},
        ]
        mock_response.raise_for_status.return_value = None
        mock.return_value = mock_response
        yield mock

@pytest.fixture
def mock_requests_delete():
    with patch('requests.delete') as mock_delete:
        success_response = MagicMock()
        success_response.status_code = 204
        success_response.raise_for_status.return_value = None
        not_found_response = MagicMock()
        not_found_response.status_code = 404
        not_found_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=not_found_response
        )
        mock_delete.return_value = success_response
        mock_delete.not_found_response = not_found_response
        yield mock_delete

# --- Test CLI Commands ---

def test_cli_add_item_success(mock_requests_post):
    """Tests the 'add-item' command successful execution."""
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'add-item', 'TestItem', '10', '100']

    main()
    sys.stdout = sys.__stdout__ # Restore stdout
    assert "Item added successfully via API" in captured_output.getvalue()

def test_cli_display_all_success(mock_api_server):
    """Tests the 'display-inventory' command."""
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'display-inventory']
    main()
    sys.stdout = sys.__stdout__
    assert "Apple" in captured_output.getvalue()

def test_cli_display_item_found(mock_requests_get):
    """Tests the 'display-item' command for an existing item."""
    mock_requests_get.return_value.json.return_value = {"id": 1, "name": "Apple", "price": 1.5, "stock": 100}
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'display-item', '1']
    main()
    sys.stdout = sys.__stdout__
    assert "name: Apple" in captured_output.getvalue()

def test_cli_display_item_not_found(mock_requests_get):
    """Tests the 'display-item' command for a non-existent item."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Item not found"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_get.return_value = mock_response
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'display-item', '99']
    main()
    sys.stdout = sys.__stdout__
    assert "Item not found" in captured_output.getvalue()

def test_cli_delete_item_success(mock_requests_delete):
    """Tests the 'delete-item' command successful execution."""
    mock_requests_delete.return_value = mock_requests_delete.success_response
    if mock_requests_delete.return_value.status_code != 204:
        mock_requests_delete.return_value.status_code = 204
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'delete-item', '5']
    main()
    sys.stdout = sys.__stdout__
    assert "Item ID 5 deleted successfully" in captured_output.getvalue()
    assert "Status 204" in captured_output.getvalue()

def test_cli_delete_item_not_found(mock_requests_delete):
    """Tests the 'delete-item' command when the item doesn't exist."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Item not found"}
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_delete.return_value = mock_response
    captured_output = StringIO()
    sys.stdout = captured_output
    sys.argv = ['main.py', 'delete-item', '99']
    main()
    sys.stdout = sys.__stdout__
    assert "Item ID 99 not found" in captured_output.getvalue()


def test_cli_find_item_success(mock_api_server):
    """Tests the 'find-item' command success (simulating server fetching external API)."""
    mock_api_server.post(f"https://world.openfoodfacts.net/api/v2/product/3017624010701?fields=product_name,nutriscore_data", json={"grade": 'e', "name": "Nutella Ferrero"}, status_code=201)

    result = run_cli_command(["find-item", "3017624010701"])

    assert result.returncode == 0
    assert "fetched and added item" in result.stdout

def test_cli_find_item_failure(mock_api_server):
    mock_api_server.post(f"https://world.openfoodfacts.net/api/v2/product/3017624010701?fields=product_name,nutriscore_data", status_code=400)
    result = run_cli_command(["find-item", "301762482094"])

    assert "ERROR: Barcode" in result.stdout