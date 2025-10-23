from pupdb.core import PupDB
import hashlib

#db
users_db = PupDB("users.json")
products_db = PupDB("products.json")

#băm mkhau
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#admin
if "admin" not in users_db.keys():
    users_db.set("admin", {"password": hash_password("1234"), "role": "admin"})