import json
import os
import requests

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {DATA_FILE} contains invalid JSON. Returning empty list.")
        return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving data to {DATA_FILE}: {e}")

def fetch_inventory(barcode, inv):
    URL = f"https://world.openfoodfacts.net/api/v2/product/{barcode}?fields=product_name,nutriscore_data"
    try:
        response = requests.get(URL)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return (f"Error: Failed to fetch data from API: {e}")

    new_id = max((i["id"] for i in inv), default=0) + 1
    new_item = {"id": new_id, "title": data["product"]["product_name"]}
    inv.append(new_item)
    print(new_item)