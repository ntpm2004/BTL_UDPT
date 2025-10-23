from flask import Flask, request, jsonify
from pupdb.core import PupDB
import threading
import requests
import time

app = Flask(__name__)
db = PupDB("products_worker1.json")

# Địa chỉ của master server
MASTER_URL = "http://127.0.0.1:5000/sync_from_worker"

@app.route("/do_task", methods=["POST"])
def do_task():
    data = request.get_json()
    action = data.get("action")
    value = data.get("value")
    subset = data.get("data", {})

    # Tạo luồng xử lý riêng để không block Flask
    thread = threading.Thread(target=process_task, args=(action, value, subset))
    thread.start()
    return jsonify({"status": "processing"}), 200


def process_task(action, value, subset):
    print(f"[Worker] Đang xử lý {len(subset)} sản phẩm...")
    updated_data = {}

    for pid, product in subset.items():
        time.sleep(0.05)  # mô phỏng thời gian xử lý
        if action == "discount":
            product["price"] = max(product["price"] - value, 0)
        elif action == "increase":
            product["price"] += value
        db.set(pid, product)
        updated_data[pid] = product

    print("[Worker 3] Hoàn tất — gửi kết quả về master...")

    try:
        res = requests.post(MASTER_URL, json={"data": updated_data})
        if res.status_code == 200:
            print("[Worker 3] Đồng bộ với master thành công")
        else:
            print(f"[Worker 3] Lỗi khi đồng bộ với master: {res.text}")
    except Exception as e:
        print(f"[Worker 3] Không thể kết nối master: {e}")


if __name__ == "__main__":
    app.run(port=7102)