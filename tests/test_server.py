import pytest
import json
from unittest.mock import patch, MagicMock

# --- Test API Endpoints (GET, POST, PATCH, DELETE) ---

# Test GET All (GET /inventory)
def test_get_all_inventory(client, mock_inventory_data):
    """Tests fetching all inventory items."""
    response = client.get('/inventory')
    assert response.status_code == 200
    assert response.get_json()

# Test GET Single Item (GET /inventory/<id>)
def test_get_single_item_success(client):
    """Tests fetching a single existing item."""
    response = client.get('/inventory/1')
    assert response.status_code == 200
    assert response.get_json()['name'] == 'Bread'

def test_get_single_item_not_found(client):
    """Tests fetching a non-existent item."""
    response = client.get('/inventory/99')
    assert response.status_code == 404
    assert 'error' in response.get_json()

# Test POST Add Item (POST /inventory)
def test_add_new_item_success(client):
    """Tests adding a new item via POST."""
    new_item_data = {"name": "Cherry", "price": 3.00, "stock": 50}
    response = client.post('/inventory', json=new_item_data)

    assert response.status_code == 201
    assert response.get_json()['name'] == 'Cherry'
    # Check that the ID auto-incremented correctly
    assert response.get_json()['stock'] == 50

def test_add_new_item_missing_field(client):
    """Tests POST failure with missing data."""
    incomplete_data = {"name": "Grape", "price": 4.00}
    response = client.post('/inventory', json=incomplete_data)

    assert response.status_code == 400
    assert 'missing' in response.get_json().get('error', '').lower()

# Test PATCH Update Item (PATCH /inventory/<id>)
def test_update_item_success(client):
    """Tests updating an existing item."""
    update_data = {"price": 1.99, "stock": 90}
    response = client.patch('/inventory/1', json=update_data)

    assert response.status_code == 200
    assert response.get_json()['price'] == 1.99
    assert response.get_json()['stock'] == 90

def test_update_item_not_found(client):
    """Tests updating a non-existent item."""
    response = client.patch('/inventory/99', json={"price": 10})
    assert response.status_code == 404

# Test DELETE Item (DELETE /inventory/<id>)
def test_delete_item_success(client):
    """Tests deleting an existing item."""
    response = client.delete('/inventory/2')
    assert response.status_code == 204

    check_response = client.get('/inventory/2')
    assert check_response.status_code == 404

def test_delete_item_not_found(client):
    """Tests deleting a non-existent item."""
    response = client.delete('/inventory/99')
    assert response.status_code == 404
