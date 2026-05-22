from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
import pyodbc
import hashlib
import os

app = Flask(__name__)
app.secret_key = "nexus_super_secret_key_2025"  # مطلوب للـ session
CORS(app, supports_credentials=True)

# 🔗 اتصال بـ SQL Server
conn = pyodbc.connect(
    "DRIVER={SQL Server};SERVER=DESKTOP-9KIIRGV;DATABASE=NexusDB;Trusted_Connection=yes;"
)

# ============================================================
# 🔒 HELPERS
# ============================================================

def hash_password(password: str) -> str:
    """SHA-256 hash لكلمة المرور"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_cursor():
    return conn.cursor()

# ============================================================
# 🌐 SERVE HTML FILES
# ============================================================

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ============================================================
# 👤 AUTH — REGISTER
# ============================================================

@app.route("/register", methods=["POST"])
def register():
    data     = request.json
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    cursor = get_cursor()

    # التحقق من عدم تكرار الـ username أو email
    cursor.execute(
        "SELECT user_id FROM Users WHERE username = ? OR email = ?",
        (username, email)
    )
    if cursor.fetchone():
        return jsonify({"message": "Username or email already exists"}), 409

    pw_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, pw_hash)
    )
    conn.commit()

    # جلب الـ user الجديد
    cursor.execute(
        "SELECT user_id, username, email FROM Users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    session["user_id"]  = row[0]
    session["username"] = row[1]
    session["email"]    = row[2]

    return jsonify({
        "message":  "Registration successful",
        "user_id":  row[0],
        "username": row[1],
        "email":    row[2]
    }), 201


# ============================================================
# 🔑 AUTH — LOGIN
# ============================================================

@app.route("/login", methods=["POST"])
def login():
    data       = request.json
    identifier = (data.get("identifier") or "").strip()   # username أو email
    password   = data.get("password", "")

    if not identifier or not password:
        return jsonify({"message": "Username/email and password are required"}), 400

    pw_hash = hash_password(password)
    cursor  = get_cursor()
    cursor.execute(
        """SELECT user_id, username, email
           FROM Users
           WHERE (username = ? OR email = ?) AND password_hash = ?""",
        (identifier, identifier.lower(), pw_hash)
    )
    row = cursor.fetchone()

    if not row:
        return jsonify({"message": "Invalid credentials"}), 401

    session["user_id"]  = row[0]
    session["username"] = row[1]
    session["email"]    = row[2]

    return jsonify({
        "message":  "Login successful",
        "user_id":  row[0],
        "username": row[1],
        "email":    row[2]
    })


# ============================================================
# 🚪 AUTH — LOGOUT
# ============================================================

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


# ============================================================
# 🙋 AUTH — CURRENT USER
# ============================================================

@app.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 200
    return jsonify({
        "logged_in": True,
        "user_id":   session["user_id"],
        "username":  session["username"],
        "email":     session["email"]
    })


# ============================================================
# 🎮 GET ALL GAMES
# ============================================================

@app.route("/games", methods=["GET"])
def get_games():
    cursor = get_cursor()
    cursor.execute("""
        SELECT g.game_id, g.name, g.price, c.name, g.stock_quantity, p.name, g.release_date
        FROM Games g 
        JOIN Categories c ON g.category_id = c.category_id
        JOIN Platforms p  ON g.platform_id  = p.platform_id
    """)
    games = []
    for row in cursor.fetchall():
        release = ""
        if row[6]:
            try:
                release = row[6].strftime("%Y-%m-%d")
            except:
                release = str(row[6])

        games.append({
            "id":             row[0],
            "name":           row[1],
            "price":          float(row[2]),
            "genre":          row[3],
            "stock_quantity": row[4],
            "platform":       row[5],
            "release_date":   release
        })

    return jsonify(games)


# ============================================================
# 🛒 BUY / MAKE ORDER
# ============================================================

@app.route("/buy", methods=["POST"])
def buy():
    data    = request.json
    items   = data.get("items", [])
    user_id = session.get("user_id")   # None لو Guest

    if not items:
        return jsonify({"message": "Cart is empty"}), 400

    cursor = get_cursor()

    try:
        total_order_price = 0
        valid_items       = []

        for item in items:
            game_id  = item.get("game_id")
            quantity = item.get("quantity")

            cursor.execute(
                "SELECT stock_quantity, price FROM Games WHERE game_id = ?",
                (game_id,)
            )
            row = cursor.fetchone()

            if not row:
                return jsonify({"message": f"Game not found (ID: {game_id})"}), 404

            stock, price = row

            if stock < quantity:
                return jsonify({"message": f"Not enough stock for Game ID: {game_id}"}), 400

            total_order_price += price * quantity
            valid_items.append({
                "game_id":  game_id,
                "quantity": quantity,
                "price":    price
            })

        # 🧾 إنشاء الأوردر مع ربطه بالمستخدم إن وُجد
        cursor.execute(
            "INSERT INTO Orders (user_id, total_price) OUTPUT INSERTED.order_id VALUES (?, ?)",
            (user_id, total_order_price)
        )
        order_id = int(cursor.fetchone()[0])

        # 📦 إدخال تفاصيل الأوردر وتحديث المخزون
        for v in valid_items:
            cursor.execute("""
                INSERT INTO Order_Items (order_id, game_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, v["game_id"], v["quantity"], v["price"]))

            cursor.execute("""
                UPDATE Games
                SET stock_quantity = stock_quantity - ?
                WHERE game_id = ?
            """, (v["quantity"], v["game_id"]))

        conn.commit()

        return jsonify({
            "message":  "Order completed successfully",
            "order_id": order_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            "message": "An error occurred during purchase",
            "error":   str(e)
        }), 500


# ============================================================
# 📋 GET ALL ORDERS
# ============================================================

@app.route("/orders", methods=["GET"])
def get_all_orders():
    cursor = get_cursor()

    cursor.execute("""
        SELECT o.order_id, o.order_date, o.total_price,
               oi.game_id, g.name, oi.quantity, oi.price
        FROM Orders o
        LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
        LEFT JOIN Games g        ON oi.game_id  = g.game_id
        ORDER BY o.order_id DESC
    """)

    orders_dict = {}

    for row in cursor.fetchall():
        order_id   = row[0]
        order_date = ""

        if row[1]:
            try:
                order_date = row[1].strftime("%Y-%m-%d %H:%M")
            except:
                order_date = str(row[1])

        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "order_id":    order_id,
                "order_date":  order_date,
                "total_price": float(row[2]) if row[2] is not None else 0.0,
                "items":       []
            }

        if row[3] is not None:
            orders_dict[order_id]["items"].append({
                "game_id":  row[3],
                "name":     row[4] if row[4] else "Unknown/Deleted Game",
                "quantity": int(row[5])   if row[5] is not None else 0,
                "price":    float(row[6]) if row[6] is not None else 0.0
            })

    return jsonify(list(orders_dict.values()))


# ============================================================
# 📋 GET MY ORDERS (للمستخدم المسجّل فقط)
# ============================================================

@app.route("/my-orders", methods=["GET"])
def get_my_orders():
    if "user_id" not in session:
        return jsonify({"message": "Not logged in"}), 401

    user_id = session["user_id"]
    cursor  = get_cursor()

    cursor.execute("""
        SELECT o.order_id, o.order_date, o.total_price,
               oi.game_id, g.name, oi.quantity, oi.price
        FROM Orders o
        LEFT JOIN Order_Items oi ON o.order_id = oi.order_id
        LEFT JOIN Games g        ON oi.game_id  = g.game_id
        WHERE o.user_id = ?
        ORDER BY o.order_id DESC
    """, (user_id,))

    orders_dict = {}

    for row in cursor.fetchall():
        order_id   = row[0]
        order_date = ""
        if row[1]:
            try:
                order_date = row[1].strftime("%Y-%m-%d %H:%M")
            except:
                order_date = str(row[1])

        if order_id not in orders_dict:
            orders_dict[order_id] = {
                "order_id":    order_id,
                "order_date":  order_date,
                "total_price": float(row[2]) if row[2] is not None else 0.0,
                "items":       []
            }

        if row[3] is not None:
            orders_dict[order_id]["items"].append({
                "game_id":  row[3],
                "name":     row[4] if row[4] else "Unknown/Deleted Game",
                "quantity": int(row[5])   if row[5] is not None else 0,
                "price":    float(row[6]) if row[6] is not None else 0.0
            })

    return jsonify(list(orders_dict.values()))


# ============================================================
# 🚀 RUN
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)