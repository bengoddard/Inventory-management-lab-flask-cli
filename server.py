from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

inventory = [
    {"id": 1, "title": "Bread"},
    {"id": 2, "title": "Peanut Butter"}
]

@app.route("/inventory", methods=["GET"])
def welcome():
    return jsonify(inventory), 200

@app.route("/inventory/<int:id>", methods=["GET"])
def display(id):
    for i in inventory:
        if i["id"] == id:
            return jsonify(i), 200
        else:
            return ("Item not found")


@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json()
    new_id = max((i["id"] for i in inventory), default=0) + 1
    if "title" not in data or not data["title"]:
        return ("Missing required field: title"), 400
    else:
        new_item = {"id": new_id, "title": data["title"]}
        inventory.append(new_item)
    if new_item:
        return jsonify(new_item), 201
    else:
        return ("Item not found"), 400

@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_item(id):
    data = request.get_json()
    item = next((i for i in inventory if i.id == id), None)
    if not item:
        return ("Item not found", 404)
    if "title" in data:
        item.title = data["title"]
    return jsonify(item)

@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_item(id):
    global inventory
    item = next((i for i in inventory if i.id == id), None)
    if not item:
        return ("Item not found", 404)
    inventory = [i for i in inventory if i.id != id]
    return ("Item deleted", 204)

if __name__ == "__main__":
    app.run(debug=True)
