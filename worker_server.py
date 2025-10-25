from flask import Flask, request, jsonify
import requests
from threading import Thread
import json
import os
import math
import unicodedata

app = Flask(__name__)

DB_FILE = "products.json"

WORKERS = [
    "http://127.0.0.1:7101",
    "http://127.0.0.1:7102",
    "http://127.0.0.1:7103"
]

def remove_accents(text):
    if not isinstance(text, str):
        return text
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def remove_accents_from_dict(data):
    if isinstance(data, dict):
        return {remove_accents(k): remove_accents_from_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_accents_from_dict(i) for i in data]
    else:
        return remove_accents(data) 
    
# ham xu ly file
def load_products():
    """Đọc tất cả sản phẩm từ file JSON"""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Error reading JSON file, returning empty dict.")
        return {}

def save_products(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)

def broadcast_to_workers(data, source_url=None):
    """Gửi bản cập nhật đến tất cả worker khác"""
    for url in WORKERS:
        if url == source_url:
            continue
        try:
            res = requests.post(f"{url}/sync", json={"data": data}, timeout=10)
            if res.status_code == 200:
                print(f"Đã đồng bộ {len(data)} sản phẩm đến {url}")
            else:
                print(f"Lỗi đồng bộ tới {url}: {res.status_code}")
        except Exception as e:
            print(f"Không thể gửi đồng bộ tới {url}: {e}")

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

    print(f" Tổng {total} sản phẩm → chia thành {len(chunks)} phần cho {len(WORKERS)} worker")

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
            print(f" Worker {url} không phản hồi: {e}")

@app.route("/task", methods=["POST"])
def receive_task():
    task = request.get_json()
    Thread(target=distribute_task, args=(task,)).start()
    return jsonify({"status": "accepted"}), 202

@app.route("/sync", methods=["POST"])
def sync_from_worker():
    body = request.get_json()
    new_data = body.get("data", {})
    source = request.remote_addr
    all_data = load_products()

    all_data.update(new_data)
    save_products(all_data)

    print(f"Đã đồng bộ {len(new_data)} sản phẩm từ worker về master")

    # Gửi lại dữ liệu này cho các worker khác
    broadcast_to_workers(new_data)

    return jsonify({"status": "synced"}), 200

@app.route("/delete_sync", methods=["POST"])
def delete_sync():
    pid = request.get_json().get("id")
    if not pid:
        return jsonify({"error": "no id"}), 400

    all_data = load_products()
    if pid in all_data:
        del all_data[pid]
        save_products(all_data)
        print(f"Đã xóa sản phẩm {pid} tại master")

    # Gửi yêu cầu xóa đến các worker khác
    for url in WORKERS:
        try:
            requests.post(f"{url}/delete_sync", json={"id": pid}, timeout=10)
        except:
            pass
    return jsonify({"status": "deleted"}), 200

#dong bo dlieu 3 wk tra ve
def sync_all_workers():
    """Lấy dữ liệu từ tất cả worker về và hợp nhất lại"""
    merged = {}
    for url in WORKERS:
        try:
            res = requests.get(f"{url}/export_data", timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", {})
                merged.update(data)
                print(f" Nhận {len(data)} sản phẩm từ {url}")
            else:
                print(f"⚠️ Worker {url} trả mã lỗi {res.status_code}")
        except Exception as e:
            print(f" Không thể kết nối {url}: {e}")

    save_products(merged)
    print(f" Đã đồng bộ tổng cộng {len(merged)} sản phẩm về {DB_FILE}")

@app.route("/sync_all", methods=["GET"])
def sync_all_route():
    """API gọi để đồng bộ toàn bộ dữ liệu"""
    Thread(target=sync_all_workers).start()
    return jsonify({"status": "sync_started"}), 200

if __name__ == "__main__":
    app.run(port=7001)