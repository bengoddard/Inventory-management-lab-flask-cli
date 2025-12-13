from flask import Flask, jsonify, request
from .utils import load_data, save_data


app = Flask(__name__)

@app.route("/inventory", methods=["GET"])
def welcome():
    inventory = load_data()
    return jsonify(inventory), 200

@app.route("/inventory/<int:id>", methods=["GET"])
def display(id):
    inventory = load_data()
    item = next((i for i in inventory if i['id'] == id), None)
    if item:
        return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404


@app.route("/inventory", methods=["POST"])
def add_item():
    inventory = load_data()
    data = request.get_json()
    if not all(k in data for k in ["name", "price", "stock"]):
         return jsonify({"error": "Missing required fields"}), 400
    new_id = max((i["id"] for i in inventory), default=0) + 1
    new_item = {"id": new_id, "name": data['name'], "price": data['price'], "stock": data['stock']}
    if new_item:
        inventory.append(new_item)
        save_data(inventory)
        return jsonify(new_item), 201
    else:
        return ("Item not found"), 400

@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_item(id):
    inventory = load_data()
    data = request.get_json()
    item = next((i for i in inventory if i['id'] == id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    if 'price' in data: item['price'] = data['price']
    if 'stock' in data: item['stock'] = data['stock']
    save_data(inventory)
    return jsonify(item), 200


@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_item(id):
    inventory = load_data()
    item_index = next((i for i, item in enumerate(inventory) if item['id'] == id), None)
    if item_index is None:
        return jsonify({"error": "Item not found"}), 404
    inventory.pop(item_index)
    save_data(inventory)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)