import json
import os
import requests

DATA_FILE = "data.json"
URL = "http://127.0.0.1:5000/inventory"

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    except json.JSONDecodeError:
        print(f"Warning: {DATA_FILE} contains invalid JSON. Returning empty list.")
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving data to {DATA_FILE}: {e}")


inventory = load_data()

def welcome_cli(args):
    try:
        response = requests.get(URL)
        inventory_data = response.json()
        if not inventory_data:
            print("Inventory is empty.")
        for item in inventory_data:
            print(f"ID: {item['id']}, Name: {item['name']}, Price: ${item['price']}, Stock: {item['stock']}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to the server at {URL}. Is your Flask server running?")

def display_item_cli(args):
    url = f"{URL}/{args.id}"

    try:
        response = requests.get(url)
        item = response.json()
        for key, value in item.items():
            print(f"{key}: {value}")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"ERROR: Item ID {args.id} not found on server.")
        else:
            print(f"API Error: {e}")

def add_item_cli(args):
    data = {
        "name": args.name,
        "price": args.price,
        "stock": args.stock
    }
    try:
        response = requests.post(URL, json=data)
        new_item = response.json()
        inventory.append(new_item)
        save_data(inventory)
        print(f"Item added successfully via API: {args.name}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to communicate with server at {URL}. Is the server running?")

def update_item_cli(args):
    url = f"{URL}/{args.id}"
    data = {
        "price": args.price,
        "stock": args.stock
    }
    try:
        response = requests.patch(url, json=data)
        updated_item = response.json()
        print(f"SUCCESS: Item ID {args.id} updated successfully.")
        print(f"New Price: ${updated_item['price']}, New Stock: {updated_item['stock']}")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"ERROR: Item ID {args.id} not found for update.")
        else:
            print("API failed during PATCH request.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to server: {e}")

def delete_item_cli(args):
    url = f"{URL}/{args.id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        print(f"SUCCESS: Item ID {args.id} deleted successfully (Status 204).")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"ERROR: Item ID {args.id} not found for deletion.")
        else:
            print("API failed during DELETE request.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to server: {e}")

def fetch_inventory_cli(args):
    url = f"https://world.openfoodfacts.net/api/v2/product/{args.barcode}?fields=product_name,nutriscore_data"
    try:
        response = requests.get(url)
        response.raise_for_status()
        new_item = response.json()
        if 'product' not in new_item or new_item.get('status', 0) == 0:
             raise requests.exceptions.HTTPError(
                 '404 Client Error: Not Found for URL: Barcode not found in Open Food Facts API.',
                 response=response
             )
        new_id = max((i["id"] for i in inventory), default=0) + 1
        price = 5
        stock = 10
        add_item = {
            "id": new_id,
            "name": new_item["product"]["product_name"],
            "price": price,
            "stock": stock
            }
        inventory.append(add_item)
        save_data(inventory)
        print(f"SUCCESS: Server fetched and added item.")
        print(f"Name: {new_item['product']['product_name']}, Grade: {new_item['product']['nutriscore_data']['grade']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404 or "Barcode not found" in str(e):
            print(f"ERROR: Barcode '{args.barcode}' not found in the external API.")
        else:
            print(f"Server failed to fetch product from external API. Status: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to external API: {e}")
