from flask import Flask, jsonify, request, abort


app = Flask(__name__)
app.config["SECRET_KEY"] = "test"

test_dict = [
    {"1": "test1"},
    {"2": "test2"},
    {"3": "test3"},
    {"4": "test4"}
]


def get_item_or_404(index):
    try:
        return test_dict[index]
    except IndexError:
        abort(404, description=f"Item index {index} not found")


@app.route("/api/get/<int:notes_index>")
def get_dict(notes_index):
    item = get_item_or_404(notes_index)
    return jsonify(item)


@app.route("/api/test", methods=["POST"])
def create_test():
    data = request.get_json()

    if not data or not isinstance(data, dict):
        abort(400, description="Invalid JSON data provided")

    test_dict.append(data)
    return jsonify({"message": "Item created", "item": data}), 201


@app.route("/api/delete/<int:notes_index>", methods=["DELETE"])
def delete_dict(notes_index):
    get_item_or_404(notes_index)
    del test_dict[notes_index]
    return jsonify({"message": f"Item at index {notes_index} deleted",
                    "remaining_items": test_dict})


@app.route("/api/put/<int:notes_index>", methods=["PUT"])
def edit_dict(notes_index):
    data = request.get_json()

    if not data or not isinstance(data, dict):
        abort(400,
              description="Invalid JSON data provided. Must be a dictionary.")

    get_item_or_404(notes_index)

    test_dict[notes_index] = data
    return jsonify({"message": f"Item at index {notes_index} fully "
                               f"replaced", "new_item": data}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "description": str(error)}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "description": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)