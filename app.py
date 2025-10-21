from flask import Flask, session
from auth import auth_bp
from product import products_bp
import requests

app = Flask(__name__)
app.secret_key = "mysecret"

# Đăng ký blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)

def remote_discount(value):
    """Gửi yêu cầu giảm giá đến worker"""
    try:
        res = requests.post(
            "http://127.0.0.1:7001/task",
            json={"action": "discount", "value": value}
        )
        if res.status_code == 202:
            print("Gửi nhiệm vụ giảm giá thành công!")
        else:
            print(f"Worker trả lỗi: {res.status_code}")
    except Exception as e:
        print(f"Lỗi khi gọi worker: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)