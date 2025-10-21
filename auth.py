from flask import Blueprint, render_template, request, redirect, url_for, session
from database import users_db, hash_password

auth_bp = Blueprint("auth", __name__)

# Đăng ký
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        if username in users_db.keys():
            return render_template("register.html", error="Tên người dùng đã tồn tại!")
        users_db.set(username, {"password": password, "role": "user"})
        return redirect(url_for("auth.login"))
    return render_template("register.html")

# Đăng nhập
@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        data = users_db.get(username)
        if data and data["password"] == password:
            session["user"] = username
            session["role"] = data["role"]
            if data["role"] == "admin":
                return redirect(url_for("products.admin_panel"))
            else:
                return redirect(url_for("products.view_products"))
        return render_template("login.html", error="Sai tài khoản hoặc mật khẩu!")
    return render_template("login.html")

# Đăng xuất
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))