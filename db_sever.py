from pupdb.core import PupDB
from flask import Flask, jsonify, request

app = Flask(__name__)
db = PupDB("distributed_db.json")

@app.route("/api/get/<key>")
def get_value(key):
    try:
        return jsonify({key: db.get(key)})
    except KeyError:
        return jsonify({"error": "Key not found"}), 404

@app.route("/api/set", methods=["POST"])
def set_value():
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")
    db.set(key, value)
    return jsonify({"message": f"Set {key} successfully!"})

@app.route("/api/keys")
def all_keys():
    return jsonify(list(db.keys()))

if __name__ == "__main__":
    print("🚀 PupDB server chạy tại http://127.0.0.1:7000")
    app.run(port=7000)