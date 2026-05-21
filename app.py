from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pyodbc
import os

app = Flask(__name__)
CORS(app)

# 🔗 اتصال بـ SQL Server
conn = pyodbc.connect(
    "DRIVER={SQL Server};SERVER=DESKTOP-9KIIRGV;DATABASE=ProjectDB;Trusted_Connection=yes;"
)

# ============================================================
# 🌐 SERVE HTML FILES
# ============================================================

@app.route("/")
def index():
    return send_from_directory(".", "game-store.html")

@app.route("/orders-page")
def orders_page():
    return send_from_directory(".", "orders.html")

# ============================================================
# 🎮 GET ALL GAMES
# ============================================================

@app.route("/games", methods=["GET"])
def get_games():
    cursor = conn.cursor()
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
    data  = request.json
    items = data.get("items", [])

    if not items:
        return jsonify({"message": "Cart is empty"}), 400

    cursor = conn.cursor()

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

        # 🧾 إنشاء الأوردر
        cursor.execute(
            "INSERT INTO Orders (total_price) OUTPUT INSERTED.order_id VALUES (?)",
            (total_order_price,)
        )

        # 🆔 جلب order_id
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
    cursor = conn.cursor()

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

        if row[3] is not None:  # التأكد من وجود اللعبة فعلياً في جدول عناصر الطلب
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