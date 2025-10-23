from flask import Flask, request, jsonify
from pupdb.core import PupDB
import threading
import time

app = Flask(__name__)
db = PupDB("products.json")

@app.route("/do_task", methods=["POST"])
def do_task():
    data = request.get_json()
    action = data.get("action")
    value = data.get("value")
    subset = data.get("data", {})

    thread = threading.Thread(target=process_task, args=(action, value, subset))
    thread.start()
    return jsonify({"status": "processing"}), 200

def process_task(action, value, subset):
    print(f"⚙️ Worker đang xử lý {len(subset)} sản phẩm...")

    for pid, product in subset.items():
        time.sleep(0.05)  # mô phỏng xử lý lâu
        if action == "discount":
            product["price"] = max(product["price"] - value, 0)
        elif action == "update_prices":
            product["price"] += value
        db.set(pid, product)  # ✅ Ghi trực tiếp lại vào file JSON

    print("✅ Worker 1 hoàn thành và đã cập nhật products.json")

if __name__ == "__main__":
    app.run(port=7101)  # ⚠️ đổi port 7102, 7103 cho worker2, worker3