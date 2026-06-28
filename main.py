

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-this")

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# MongoDB Connection
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    db = client["otppp_db"]
    users_collection = db["users"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    db = None
    users_collection = None

# Counter for auto-increment IDs
def get_next_id(counter_name):
    """Get next auto-increment ID from counters collection."""
    if db is None:
        return 1
    result = db.counters.find_one_and_update(
        {"_id": counter_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]


# ============================================================
# IMPORT AND REGISTER ALL BLUEPRINTS (ROUTES)
# ============================================================

# 1. Landing Page (index.py)
from routes.index import init_index
app.register_blueprint(init_index())

# 2. Auth Routes (signup.py, login.py)
from routes.auth.signup import init_signup
from routes.auth.login import init_login
app.register_blueprint(init_signup(users_collection, bcrypt, get_next_id))
app.register_blueprint(init_login(users_collection, bcrypt))

# 3. Dashboard Route
from routes.dashboard import init_dashboard
app.register_blueprint(init_dashboard(users_collection, db))

# 4. Admin Routes
from routes.admin.admin import init_admin
from routes.admin.admin_add import init_admin_add
from routes.admin.admin_services import init_admin_services
app.register_blueprint(init_admin(db))
app.register_blueprint(init_admin_add(db))
app.register_blueprint(init_admin_services(db))

# 5. Currency API
from routes.currency import currency_bp
app.register_blueprint(currency_bp)


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":
    print("🚀 Starting OTPPP Server...")
    print("📍 URL: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
'''

with open("/mnt/agents/output/otppp/main.py", "w") as f:
    f.write(main_py)

print("✅ main.py created!")
