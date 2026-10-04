from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_NAME = "marketplace.db"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# INITIALIZE DATABASE
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            village TEXT,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            name TEXT NOT NULL,
            category TEXT,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            buyer_name TEXT,
            quantity REAL,
            total_price REAL,
            order_date TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    conn.close()


# HOME ROUTE
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Farmer Direct Marketplace API is running!",
        "status": "success"
    })


# REGISTER FARMER
@app.route("/farmers", methods=["POST"])
def add_farmer():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({"error": "Farmer name is required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO farmers (name, village, phone)
        VALUES (?, ?, ?)
    """, (
        data["name"],
        data.get("village"),
        data.get("phone")
    ))

    farmer_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Farmer registered successfully",
        "farmer_id": farmer_id
    }), 201


# GET ALL FARMERS
@app.route("/farmers", methods=["GET"])
def get_farmers():
    conn = get_db()

    farmers = conn.execute(
        "SELECT * FROM farmers"
    ).fetchall()

    conn.close()

    return jsonify([dict(farmer) for farmer in farmers])


# ADD PRODUCT
@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()

    required = ["farmer_id", "name", "quantity", "price"]

    if not data or any(key not in data for key in required):
        return jsonify({"error": "Missing required fields"}), 400

    if data["quantity"] <= 0 or data["price"] < 0:
        return jsonify({"error": "Invalid quantity or price"}), 400

    conn = get_db()
    cursor = conn.cursor()

    farmer = cursor.execute(
        "SELECT id FROM farmers WHERE id = ?",
        (data["farmer_id"],)
    ).fetchone()

    if not farmer:
        conn.close()
        return jsonify({"error": "Farmer not found"}), 404

    cursor.execute("""
        INSERT INTO products
        (farmer_id, name, category, quantity, price, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["farmer_id"],
        data["name"],
        data.get("category", "General"),
        data["quantity"],
        data["price"],
        data.get("latitude"),
        data.get("longitude")
    ))

    product_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Product added successfully",
        "product_id": product_id
    }), 201


# GET MARKETPLACE PRODUCTS
@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db()

    products = conn.execute("""
        SELECT
            products.*,
            farmers.name AS farmer_name,
            farmers.village
        FROM products
        JOIN farmers ON products.farmer_id = farmers.id
        WHERE products.quantity > 0
    """).fetchall()

    conn.close()

    return jsonify([dict(product) for product in products])


# PLACE ORDER
@app.route("/orders", methods=["POST"])
def place_order():
    data = request.get_json()

    if not data or not all(
        key in data for key in ["product_id", "buyer_name", "quantity"]
    ):
        return jsonify({"error": "Missing order details"}), 400

    quantity = data["quantity"]

    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return jsonify({"error": "Quantity must be positive"}), 400

    conn = get_db()
    cursor = conn.cursor()

    product = cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (data["product_id"],)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    if quantity > product["quantity"]:
        conn.close()
        return jsonify({"error": "Insufficient stock"}), 400

    total = quantity * product["price"]

    cursor.execute("""
        INSERT INTO orders
        (product_id, buyer_name, quantity, total_price, order_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["product_id"],
        data["buyer_name"],
        quantity,
        total,
        datetime.now().isoformat()
    ))

    order_id = cursor.lastrowid

    cursor.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (quantity, data["product_id"]))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Order placed successfully",
        "order_id": order_id,
        "total_price": total,
        "status": "Pending"
    }), 201


# GET ALL ORDERS
@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_db()

    orders = conn.execute("""
        SELECT
            orders.*,
            products.name AS product_name
        FROM orders
        JOIN products ON orders.product_id = products.id
        ORDER BY orders.id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(order) for order in orders])


# UPDATE ORDER STATUS
@app.route("/orders/<int:order_id>", methods=["PATCH"])
def update_order(order_id):
    data = request.get_json()
    status = data.get("status") if data else None

    allowed = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]

    if status not in allowed:
        return jsonify({"error": "Invalid order status"}), 400

    conn = get_db()
    cursor = conn.cursor()

    order = cursor.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Order status updated",
        "status": status
    })


# DEMAND FORECASTING
@app.route("/forecast/<int:product_id>", methods=["GET"])
def forecast_demand(product_id):
    conn = get_db()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    result = conn.execute("""
        SELECT
            COALESCE(SUM(quantity), 0) AS total_demand,
            COUNT(*) AS order_count
        FROM orders
        WHERE product_id = ?
        AND status != 'Cancelled'
    """, (product_id,)).fetchone()

    conn.close()

    total_demand = result["total_demand"]
    order_count = result["order_count"]

    average_order = (
        total_demand / order_count if order_count else 0
    )

    return jsonify({
        "product": product["name"],
        "historical_orders": order_count,
        "total_demand": total_demand,
        "average_order_quantity": round(average_order, 2),
        "forecast_type": "Historical average baseline",
        "note": "This is a baseline estimate, not a trained AI prediction."
    })


# ROUTE OPTIMIZATION
@app.route("/optimize-route", methods=["POST"])
def optimize_route():
    data = request.get_json()

    if not data or not isinstance(data.get("locations"), list):
        return jsonify({"error": "Provide a locations list"}), 400

    locations = data["locations"]

    if not locations:
        return jsonify({"error": "Locations cannot be empty"}), 400

    try:
        for point in locations:
            lat = float(point["latitude"])
            lon = float(point["longitude"])

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("Coordinates out of range")

            point["latitude"] = lat
            point["longitude"] = lon

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "Each location needs valid latitude and longitude"
        }), 400

    # Nearest-neighbor route heuristic
    remaining = locations.copy()
    route = [remaining.pop(0)]

    while remaining:
        current = route[-1]

        nearest = min(
            remaining,
            key=lambda point: (
                (point["latitude"] - current["latitude"]) ** 2
                + (point["longitude"] - current["longitude"]) ** 2
            )
        )

        route.append(nearest)
        remaining.remove(nearest)

    return jsonify({
        "message": "Delivery sequence generated",
        "algorithm": "Nearest Neighbor Heuristic",
        "route": route,
        "note": "Sequence is based on straight-line coordinate distance, not live road traffic."
    })


# RUN SERVER
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)