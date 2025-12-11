from flask import Flask
import requests
from .utils import load_data, save_data


app = Flask(__name__)

inventory = load_data()


def fetch_inventory(barcode):
    URL = f"https://world.openfoodfacts.net/api/v2/product/{barcode}?fields=product_name,nutriscore_data"
    try:
        response = requests.get(URL)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return (f"Error: Failed to fetch data from API: {e}")

    new_id = max((i["id"] for i in inventory), default=0) + 1
    new_item = {"id": new_id, "name": data["product"]["product_name"]}
    inventory.append(new_item)
    print(new_item)

@app.route("/inventory", methods=["GET"])
def welcome(args):
    print(inventory)

@app.route("/inventory/<int:id>", methods=["GET"])
def display(args):
    for i in inventory:
        if i["id"] == args.id:
            print(i)
    return ("Item not found")


@app.route("/inventory", methods=["POST"])
def add_item(args):
    new_id = max((i["id"] for i in inventory), default=0) + 1
    new_item = {"id": new_id, "name": args.name, "price": args.price, "stock": args.stock}
    if new_item:
        inventory.append(new_item)
        save_data(inventory)
        return new_item
    else:
        return ("Item not found"), 400

@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_item(args):
    item = next((i for i in inventory if i.id == args.id), None)
    if not item:
        return ("Item not found", 404)
    item.price += args.price
    item.stock += args.stock
    save_data(inventory)
    return item

@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_item(args):
    global inventory
    item = next((i for i in inventory if i.id == args.id), None)
    if not item:
        return ("Item not found", 404)
    inventory = [i for i in inventory if i.id != args.id]
    save_data(inventory)
    return ("Item deleted", 204)

if __name__ == "__main__":
    app.run(debug=True)