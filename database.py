from pupdb.core import PupDB
import hashlib

# Tạo các DB
users_db = PupDB("users.json")
products_db = PupDB("products.json")

# Hàm băm mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Tạo admin mặc định
if "admin" not in users_db.keys():
    users_db.set("admin", {"password": hash_password("1234"), "role": "admin"})