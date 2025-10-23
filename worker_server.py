from flask import Flask, request, jsonify
import requests
from threading import Thread
import json
import os
import math

app = Flask(__name__)

DB_FILE = "products.json"

WORKERS = [
    "http://127.0.0.1:7101",
    "http://127.0.0.1:7102",
    "http://127.0.0.1:7103"
]

def load_products():
    """Đọc toàn bộ sản phẩm từ file JSON"""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def distribute_task(task):
    action = task.get("action")
    value = task.get("value")

    all_products = load_products()
    items = list(all_products.items())
    total = len(items)

    if total == 0:
        print(" Không có sản phẩm để xử lý!")
        return

    # Chia đều sản phẩm cho worker — bao gồm cả phần dư
    chunk_size = math.ceil(total / len(WORKERS))
    chunks = [items[i:i + chunk_size] for i in range(0, total, chunk_size)]

    print(f"📦 Tổng {total} sản phẩm → chia thành {len(chunks)} phần cho {len(WORKERS)} worker")

    for i, url in enumerate(WORKERS):
        if i < len(chunks):
            subset = dict(chunks[i])
        else:
            subset = {}

        try:
            res = requests.post(
                f"{url}/do_task",
                json={"action": action, "value": value, "data": subset},
                timeout=10
            )
            print(f"Gửi task '{action}' tới {url}: {res.status_code}")
        except Exception as e:
            print(f"❌ Worker {url} không phản hồi: {e}")

@app.route("/task", methods=["POST"])
def receive_task():
    task = request.get_json()
    Thread(target=distribute_task, args=(task,)).start()
    return jsonify({"status": "accepted"}), 202

if __name__ == "__main__":
    app.run(port=7001)