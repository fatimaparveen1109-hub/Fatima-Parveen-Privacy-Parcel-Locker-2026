from db import one, execute
from config import ADMIN_EMAIL, ADMIN_PASSWORD_HASH
from services.passwords import hash_password, verify_password

def register_user(name, email, password, role):
    if role not in ("customer", "seller", "rider"): raise ValueError("Invalid role")
    if len(password) < 10: raise ValueError("Password must be at least 10 characters")
    if one("SELECT id FROM users WHERE email=%s", (email.lower().strip(),)):
        raise ValueError("Email is already registered")
    status = "pending" if role in ("seller", "rider") else "active"
    row = one("INSERT INTO users(name,email,password_hash,role,status) VALUES(%s,%s,%s,%s,%s) RETURNING id,name,email,role,status",
              (name.strip(), email.lower().strip(), hash_password(password), role, status))
    if role == "seller": execute("INSERT INTO sellers(user_id,store_name) VALUES(%s,%s)", (row['id'], name.strip()))
    if role == "rider": execute("INSERT INTO riders(user_id) VALUES(%s)", (row['id'],))
    return row

def login(email, password):
    email = email.lower().strip()
    if email == ADMIN_EMAIL and ADMIN_PASSWORD_HASH and verify_password(password, ADMIN_PASSWORD_HASH):
        return {"id": None, "name": "Administrator", "email": email, "role": "admin", "status": "active"}
    user = one("SELECT id,name,email,password_hash,role,status FROM users WHERE email=%s", (email,))
    if not user or not verify_password(password, user['password_hash']): return None
    if user['status'] != 'active': raise ValueError("Account is pending approval or suspended")
    user.pop('password_hash', None)
    return user
