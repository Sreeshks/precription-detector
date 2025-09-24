from flask import Flask, request, jsonify, render_template, session
from data_storage import medicines, cart, save_data, users, orders, generate_order_id, calculate_delivery_time, calculate_total_cost
import os
import json
import difflib
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid

# Load environment variables from .env file
load_dotenv()

try:
    import google.generativeai as genai
except Exception:  # library may not be installed yet during initial run
    genai = None

app = Flask(__name__, template_folder=".")
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

@app.after_request
def add_cors_headers(response):
    # Allow CORS for local development and file:// origin use-cases
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*') or '*'
    response.headers['Vary'] = 'Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Content-Type')
    return response

# CORS preflight for all endpoints
@app.route('/add_to_cart', methods=['OPTIONS'])
@app.route('/extract_medicines', methods=['OPTIONS'])
@app.route('/medicines', methods=['OPTIONS'])
@app.route('/login', methods=['OPTIONS'])
@app.route('/register', methods=['OPTIONS'])
@app.route('/logout', methods=['OPTIONS'])
@app.route('/get_cart', methods=['OPTIONS'])
@app.route('/update_cart', methods=['OPTIONS'])
@app.route('/remove_from_cart', methods=['OPTIONS'])
@app.route('/place_order', methods=['OPTIONS'])
@app.route('/get_orders', methods=['OPTIONS'])
@app.route('/cancel_order', methods=['OPTIONS'])
def cors_preflight():
    # Respond to preflight requests for specific endpoints
    return ('', 204)

@app.route("/")
def index():
    # Render index.html and pass medicines and current user to it
    current_user = session.get('username')
    return render_template("index.html", medicines=medicines, current_user=current_user)

@app.route("/medicines", methods=["GET"])
def get_medicines():
    # Provide a JSON endpoint for clients that open the HTML without templating
    return jsonify(medicines)

def _server_side_fuzzy_detect(text: str, med_keys):
    """Fallback detection using difflib if Gemini is unavailable."""
    text_l = text.lower()
    found = set()
    # quick contains
    for k in med_keys:
        if k.lower() in text_l:
            found.add(k)
    # token-based close matches
    tokens = [t for t in ''.join([c if c.isalpha() or c.isspace() else ' ' for c in text_l]).split() if len(t) >= 4]
    for t in set(tokens):
        close = difflib.get_close_matches(t, [mk.lower() for mk in med_keys], n=1, cutoff=0.82)
        if close:
            idx = [mk.lower() for mk in med_keys].index(close[0])
            found.add(med_keys[idx])
    return sorted(found)

@app.route("/extract_medicines", methods=["POST"])
def extract_medicines():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    med_keys = list(medicines.keys())
    if not text.strip():
        return jsonify({"detected": [], "error": "empty_text"}), 400

    api_key = os.getenv("api_key")
    if genai is None or not api_key:
        detected = _server_side_fuzzy_detect(text, med_keys)
        return jsonify({
            "detected": detected,
            "source": "fallback",
            "model": None
        })

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        sys_prompt = (
            "You extract medicine names from the provided OCR text. "
            "Only return medicines that exist in the provided 'allowed_medicines' list. "
            "Ignore non-medicine words, numbers, headers (like Medicines:, Name:, Age:). "
            "Return a compact JSON array of strings with exact values from allowed_medicines. No extra text."
        )
        prompt = (
            f"allowed_medicines = {json.dumps(med_keys)}\n\n"
            f"ocr_text = '''\n{text}\n'''\n\n"
            "Respond with JSON array only, e.g., [\"Paracetamol\", \"Ibuprofen\"]."
        )
        resp = model.generate_content([sys_prompt, prompt])
        raw = resp.text.strip() if hasattr(resp, 'text') else ''
        # try to extract JSON array
        start = raw.find('[')
        end = raw.rfind(']')
        detected = []
        if start != -1 and end != -1 and end > start:
            json_str = raw[start:end+1]
            detected = json.loads(json_str)
        if not isinstance(detected, list):
            detected = []
        # Filter to med_keys to be safe
        detected = [d for d in detected if d in medicines]
        # If empty, try fallback to difflib as a safety net
        if not detected:
            detected = _server_side_fuzzy_detect(text, med_keys)
        return jsonify({
            "detected": detected,
            "source": "gemini",
            "model": "gemini-2.0-flash-exp"
        })
    except Exception as e:
        detected = _server_side_fuzzy_detect(text, med_keys)
        return jsonify({
            "detected": detected,
            "source": "error_fallback",
            "model": None,
            "error": str(e)
        })

# Authentication endpoints
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"})
    
    if username in users:
        stored_password = users[username].get('password', '').strip()
        if stored_password.lower() == password.lower():
            session['username'] = username
            session['is_admin'] = users[username].get('is_admin', False)
            return jsonify({"success": True, "message": "Login successful", "is_admin": users[username].get('is_admin', False)})
        else:
            return jsonify({"success": False, "message": "Invalid password"})
    else:
        return jsonify({"success": False, "message": "Username not found"})

@app.route("/admin_login", methods=["POST"])
def admin_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # Only allow admin users
    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"})
    if username in users and users[username].get('is_admin', False):
        stored_password = users[username].get('password', '').strip()
        if stored_password.lower() == password.lower():
            session['username'] = username
            session['is_admin'] = True
            return jsonify({"success": True, "message": "Admin login successful", "is_admin": True})
        else:
            return jsonify({"success": False, "message": "Invalid admin password"})
    else:
        return jsonify({"success": False, "message": "Admin username not found or not an admin"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    address = data.get('address', '').strip()
    
    if not username or not password or not address:
        return jsonify({"success": False, "message": "All fields are required"})
    
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"})
    
    if username in users:
        return jsonify({"success": False, "message": "Username already exists"})
    
    users[username] = {"password": password, "address": address}
    save_data(medicines, users, orders, cart)
    return jsonify({"success": True, "message": "Registration successful"})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

# Cart management endpoints
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    # Handle both single medicine and multiple medicines
    if 'medicines' in data:  # Legacy support for prescription upload
        added = []
        for med in data.get("medicines", []):
            if med in medicines:
                cart[med] = cart.get(med, 0) + 1
                added.append(med)
        save_data(medicines, users, orders, cart)
        return jsonify({
            "success": True,
            "message": f"Added {', '.join(added)} to cart!" if added else "No valid medicines found"
        })
    else:  # Single medicine add
        medicine = data.get('medicine')
        quantity = data.get('quantity', 1)
        
        if not medicine or medicine not in medicines:
            return jsonify({"success": False, "message": "Medicine not found"})
        
        if medicines[medicine]['stock'] < quantity:
            return jsonify({"success": False, "message": "Insufficient stock"})
        
        cart[medicine] = cart.get(medicine, 0) + quantity
        save_data(medicines, users, orders, cart)
        return jsonify({"success": True, "message": f"Added {quantity} {medicine} to cart"})

@app.route("/get_cart", methods=["GET"])
def get_cart():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    return jsonify({"success": True, "cart": cart})

@app.route("/update_cart", methods=["POST"])
def update_cart():
    data = request.json
    username = data.get('username')
    medicine = data.get('medicine')
    quantity = data.get('quantity', 1)
    
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    if not medicine or medicine not in medicines:
        return jsonify({"success": False, "message": "Medicine not found"})
    
    if quantity <= 0:
        if medicine in cart:
            del cart[medicine]
    else:
        if medicines[medicine]['stock'] < quantity:
            return jsonify({"success": False, "message": "Insufficient stock"})
        cart[medicine] = quantity
    
    save_data(medicines, users, orders, cart)
    return jsonify({"success": True, "message": "Cart updated"})

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    data = request.json
    username = data.get('username')
    medicine = data.get('medicine')
    
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    if medicine in cart:
        del cart[medicine]
        save_data(medicines, users, orders, cart)
        return jsonify({"success": True, "message": "Item removed from cart"})
    
    return jsonify({"success": False, "message": "Item not found in cart"})

# Order management endpoints
@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.json
    username = data.get('username')
    prescription = data.get('prescription', '')
    
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    if not cart:
        return jsonify({"success": False, "message": "Cart is empty"})
    
    if not prescription:
        return jsonify({"success": False, "message": "Prescription details required"})
    
    # Check stock availability
    for med, qty in cart.items():
        if medicines[med]['stock'] < qty:
            return jsonify({"success": False, "message": f"Insufficient stock for {med}"})
    
    order_id = generate_order_id()
    delivery_time = calculate_delivery_time()
    total_cost = calculate_total_cost(cart, medicines)
    
    orders[order_id] = {
        "username": username,
        "items": cart.copy(),
        "prescription": prescription,
        "status": "Processing",
        "delivery_time": delivery_time,
        "total": total_cost
    }
    
    # Update stock
    for med, qty in cart.items():
        medicines[med]['stock'] -= qty
    
    cart.clear()
    save_data(medicines, users, orders, cart)
    
    return jsonify({
        "success": True,
        "message": "Order placed successfully",
        "order_id": order_id,
        "delivery_time": delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
        "total": total_cost
    })

@app.route("/get_orders", methods=["GET"])
def get_orders():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    user_orders = []
    for order_id, order in orders.items():
        if order['username'] == username:
            order_data = order.copy()
            order_data['order_id'] = order_id
            if isinstance(order_data['delivery_time'], datetime):
                order_data['delivery_time'] = order_data['delivery_time'].strftime('%Y-%m-%d %H:%M:%S')
            user_orders.append(order_data)
    
    return jsonify({"success": True, "orders": user_orders})

@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    data = request.json
    username = data.get('username')
    order_id = data.get('order_id')
    
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"})
    
    if order_id not in orders:
        return jsonify({"success": False, "message": "Order not found"})
    
    order = orders[order_id]
    if order['username'] != username:
        return jsonify({"success": False, "message": "Unauthorized"})
    
    if order['status'] != 'Processing':
        return jsonify({"success": False, "message": "Order cannot be cancelled"})
    
    # Check if within cancellation time limit (30 minutes before delivery)
    current_time = datetime.now()
    delivery_time = order['delivery_time']
    if isinstance(delivery_time, str):
        delivery_time = datetime.strptime(delivery_time, '%Y-%m-%d %H:%M:%S')
    
    time_limit = timedelta(minutes=30)
    cutoff_time = delivery_time - time_limit
    
    if current_time >= cutoff_time:
        return jsonify({"success": False, "message": "Too close to delivery time! Cancellation not allowed."})
    
    # Restore stock
    for med, qty in order['items'].items():
        if med in medicines:
            medicines[med]['stock'] += qty
    
    del orders[order_id]
    save_data(medicines, users, orders, cart)
    
    return jsonify({"success": True, "message": "Order cancelled successfully"})

# --- Admin API Endpoints ---
from flask import abort

def is_admin():
    return session.get('is_admin', False)

@app.route('/admin_add_medicine', methods=['POST'])
def admin_add_medicine():
    if not is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name', '').strip()
    try:
        price = float(data.get('price', 0))
        stock = int(data.get('stock', 0))
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid price or stock'}), 400
    if not name or price < 0 or stock < 0:
        return jsonify({'success': False, 'message': 'Invalid input'}), 400
    if name in medicines:
        return jsonify({'success': False, 'message': 'Medicine already exists'}), 400
    medicines[name] = {'price': price, 'stock': stock}
    save_data(medicines, users, orders, cart)
    return jsonify({'success': True})

@app.route('/admin_remove_medicine', methods=['POST'])
def admin_remove_medicine():
    if not is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name', '').strip()
    if not name or name not in medicines:
        return jsonify({'success': False, 'message': 'Medicine not found'}), 404
    del medicines[name]
    save_data(medicines, users, orders, cart)
    return jsonify({'success': True})

@app.route('/admin_orders', methods=['GET'])
def admin_orders():
    if not is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    all_orders = []
    for oid, order in orders.items():
        order_data = order.copy()
        order_data['order_id'] = oid
        if isinstance(order_data['delivery_time'], datetime):
            order_data['delivery_time'] = order_data['delivery_time'].strftime('%Y-%m-%d %H:%M:%S')
        all_orders.append(order_data)
    return jsonify({'success': True, 'orders': all_orders})

@app.route('/admin_update_order', methods=['POST'])
def admin_update_order():
    if not is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.json
    order_id = data.get('order_id', '').strip()
    status = data.get('status', '').strip()
    if order_id not in orders:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    if status not in ['Processing', 'Shipped', 'Delivered']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    orders[order_id]['status'] = status
    save_data(medicines, users, orders, cart)
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

