from flask import Flask, request, jsonify
from multiprocessing import Pool
from pupdb.core import PupDB
from threading import Thread
import time

app = Flask(__name__)
db = PupDB("products.json")

# Hàm cập nhật 1 sản phẩm
def update_single_product(data):
    pid, change = data
    product = db.get(pid)
    if product:
        time.sleep(1)  # mô phỏng thời gian xử lý
        product["price"] += change
        db.set(pid, product)
        print(f"Cập nhật {pid} xong! Giá mới: {product['price']}₫")
    return pid

# Hàm giảm giá 1 sản phẩm
def discount_single_product(data):
    pid, discount = data
    product = db.get(pid)
    if product:
        time.sleep(1)
        product["price"] = max(0, product["price"] - discount)
        db.set(pid, product)
        print(f"Giảm giá {pid} xong! Giá mới: {product['price']}₫")
    return pid

# Hàm chạy song song
def update_all_products_parallel(change):
    pids = db.keys()
    with Pool(processes=4) as pool:
        pool.map(update_single_product, [(pid, change) for pid in pids])
    print(" Hoàn tất cập nhật giá song song!")

def discount_all_products_parallel(discount):
    pids = db.keys()
    with Pool(processes=4) as pool:
        pool.map(discount_single_product, [(pid, discount) for pid in pids])
    print(" Hoàn tất giảm giá song song!")

# Route nhận task từ web admin
@app.route("/task", methods=["POST"])
def handle_task():
    task = request.get_json()
    action = task.get("action")
    value = task.get("value", 10)

    if action == "update_prices":
        Thread(target=update_all_products_parallel, args=(value,)).start()
        return jsonify({"status": "accepted"}), 202

    elif action == "discount":
        Thread(target=discount_all_products_parallel, args=(value,)).start()
        return jsonify({"status": "accepted"}), 202

    return jsonify({"status": "unknown task"}), 400

if __name__ == "__main__":
    print("Worker Node đang chạy tại http://127.0.0.1:7001")
    app.run(port=7001)