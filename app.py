from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

ORDERS_FILE = "order.json"

# Create order.json file if it doesn't exist
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w") as f:
        json.dump([], f)

# Generate unique order ID
def generate_order_id(existing_orders):
    count = len(existing_orders) + 1
    return f"ORD{str(count).zfill(4)}"

# Get current timestamp in IST
def get_current_ist():
    india = pytz.timezone("Asia/Kolkata")
    return datetime.now(india).strftime("%d-%m-%Y %I:%M %p")

@app.route('/')
def home():
    return "Cafe Order API is live"

@app.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.get_json()

        required_fields = ['name', 'number', 'items', 'table_id']
        if not all(field in data for field in required_fields):
            return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
        # Calculate total price
        total_price = 0
        for item in data['items']:
            price_lookup = {
                "Lounge Elegance Espresso": 35,
                "Velvet Mocha Delight": 45,
                "Caramel Macchiato Symphony": 40,
                "Butter Croissant": 20,
                "Chocolate Danish": 300,
                "Classic Mint Mojito": 120,
                "Strawberry Mojito": 150,
                "Lemon Mojito": 130,
                "Blue Curacao Mojito":60,
                "Watermelon Mojito": 140 
            }
            item_name = item['item']
            qty = item['qty']
            total_price += price_lookup.get(item_name, 0) * qty

        with open(ORDERS_FILE, "r+") as f:
            orders = json.load(f)
            order_id = generate_order_id(orders)
            timestamp = get_current_ist()

            order = {
                "order_id": order_id,
                "table_id": data["table_id"],
                "name": data["name"],
                "number": data["number"],
                "items": data["items"],
                "timestamp": timestamp
            }

            orders.append(order)
            f.seek(0)
            json.dump(orders, f, indent=2)
            f.truncate()

        return jsonify({
            'status': 'success',
            'message': 'Order received',
            'order_id': order_id,
            'timestamp': timestamp,
            'table_id': data['table_id'],
            'name': data['name'],
            'number': data['number'],
            'items': data['items'],
            'total': round(total_price, 2)
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
