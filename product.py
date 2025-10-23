from flask import Blueprint, render_template, request, redirect, url_for, session
from pupdb.core import PupDB
import requests

products_bp = Blueprint("products", __name__)
products_db = PupDB("products.json")

# Trang admin
@products_bp.route("/admin")
def admin_panel():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    try:
        products = {pid: products_db.get(pid) for pid in products_db.keys()}
    except:
        products = {}
    return render_template("admin.html", products=products)

# Thêm sản phẩm
@products_bp.route("/add_product", methods=["POST"])
def add_product():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    pid = request.form["id"]
    name = request.form["name"]
    price = int(request.form["price"])
    qty = int(request.form["quantity"])
    products_db.set(pid, {"name": name, "price": price, "quantity": qty})
    return redirect(url_for("products.admin_panel"))

# Sửa sản phẩm
@products_bp.route("/edit/<pid>")
def edit_product(pid):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    product = products_db.get(pid)
    return render_template("edit_product.html", pid=pid, product=product)

# Cập nhật sản phẩm
@products_bp.route("/update/<pid>", methods=["POST"])
def update_product(pid):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    name = request.form["name"]
    price = int(request.form["price"])
    qty = int(request.form["quantity"])
    products_db.set(pid, {"name": name, "price": price, "quantity": qty})
    return redirect(url_for("products.admin_panel"))

# Xóa sản phẩm
@products_bp.route("/delete/<pid>")
def delete_product(pid):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    products_db.remove(pid)
    return redirect(url_for("products.admin_panel"))

# Xem sản phẩm
@products_bp.route("/products")
def view_products():
    try:
        products = {pid: products_db.get(pid) for pid in products_db.keys()}
    except:
        products = {}
    return render_template("products.html", products=products)

# Gửi task giảm giá hàng loạt
@products_bp.route("/discount_all", methods=["POST"])
def discount_all():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    discount = int(request.form.get("discount", 5000))
    try:
        res = requests.post("http://127.0.0.1:7001/task", json={"action": "discount", "value": discount})
        if res.status_code == 202:
            print("Gửi nhiệm vụ giảm giá thành công!")
    except Exception as e:
        print(f"Lỗi khi gọi worker: {e}")

    return redirect(url_for("products.admin_panel"))