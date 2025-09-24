import sqlite3
from datetime import datetime, timedelta
import uuid

# Database setup
DB_NAME = "delivery.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create tables if they don't exist, removing indian_price column
    c.execute('''CREATE TABLE IF NOT EXISTS medicines 
                 (name TEXT PRIMARY KEY, price REAL, stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (order_id TEXT PRIMARY KEY, username TEXT, items TEXT, prescription TEXT, status TEXT, delivery_time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cart 
                 (medicine TEXT, quantity INTEGER, PRIMARY KEY (medicine))''')
    # Initialize with default medicines if empty
    c.execute("SELECT name FROM medicines")
    if not c.fetchall():
        default_medicines = [
            # Commonly Used Medicines
            ("Paracetamol", 10, 150),    # US: $11 -> ₹920
            ("Ibuprofen", 13, 100),     # US: $16.5 -> ₹1380
            ("Antacid",15 , 200),        # US: $8 -> ₹670
            ("Cough Syrup", 11, 80),    # US: $13.8 -> ₹1150
            ("Vitamin C", 5, 180),      # US: $6 -> ₹500
            ("Allergy Relief", 16, 60), # US: $20 -> ₹1670
            # Medicines for Serious Diseases
            ("Metformin", 23, 50),      # US: $27.5 -> ₹2300
            ("Atorvastatin", 27, 40),   # US: $33 -> ₹2750
            ("Chemotherapy Drug", 46, 20), # US: $55 -> ₹4600
            ("Insulin", 36, 30),        # US: $44 -> ₹3675
            ("Livogon", 20, 25)         # Added for prescription scanning
        ]
        c.executemany("INSERT OR IGNORE INTO medicines (name, price, stock) VALUES (?, ?, ?)", default_medicines)
    conn.commit()
    conn.close()

def save_data(medicines, users, orders, cart):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for med, details in medicines.items():
        c.execute("INSERT OR REPLACE INTO medicines (name, price, stock) VALUES (?, ?, ?)", 
                  (med, details['price'], details['stock']))
    for user, details in users.items():
        c.execute("INSERT OR REPLACE INTO users (username, password, address) VALUES (?, ?, ?)", 
                  (user, details['password'].strip(), details['address']))
    for oid, order in orders.items():
        c.execute("INSERT OR REPLACE INTO orders (order_id, username, items, prescription, status, delivery_time) VALUES (?, ?, ?, ?, ?, ?)", 
                  (oid, order['username'], str(order['items']), order['prescription'], order['status'], order['delivery_time'].strftime('%Y-%m-%d %H:%M:%S')))
    c.execute("DELETE FROM cart")  # Clear cart and reinsert
    for med, qty in cart.items():
        c.execute("INSERT INTO cart (medicine, quantity) VALUES (?, ?)", (med, qty))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Fetch medicines and convert to dictionary with nested structure
    medicines_data = c.execute("SELECT name, price, stock FROM medicines").fetchall()
    medicines = {row[0]: {"price": row[1], "stock": row[2]} for row in medicines_data}
    # Fetch users and convert to dictionary with nested structure
    users_data = c.execute("SELECT username, password, address FROM users").fetchall()
    users = {row[0]: {"password": str(row[1]).strip(), "address": row[2]} for row in users_data}
    # Fetch orders and convert to dictionary with nested structure
    orders_data = c.execute("SELECT order_id, username, items, prescription, status, delivery_time FROM orders").fetchall()
    orders = {row[0]: {"username": row[1], "items": eval(row[2]), "prescription": row[3], "status": row[4], "delivery_time": datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S')} for row in orders_data}
    # Fetch cart and convert to dictionary
    cart_data = c.execute("SELECT medicine, quantity FROM cart").fetchall()
    cart = {row[0]: row[1] for row in cart_data}
    conn.close()
    return medicines, users, orders, cart

def generate_order_id():
    return str(uuid.uuid4())[:8]

def calculate_delivery_time():
    # Set delivery time based on 3:00 PM IST cutoff
    current_time = datetime.now()
    delivery_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)  # 6:00 PM IST
    if current_time.hour < 15:  # Before 3:00 PM IST
        if current_time.hour >= 18:  # If after 6:00 PM, move to next day
            delivery_time += timedelta(days=1)
    else:  # After 3:00 PM IST
        delivery_time += timedelta(days=1)
    return delivery_time

def calculate_total_cost(items, medicines):
    total = 0
    for med, qty in items.items():
        if med in medicines and medicines[med]["stock"] >= qty:
            total += medicines[med]["price"] * qty
    delivery_fee = 417.5  # $5 * 83.5 = ₹417.5
    return total + delivery_fee

# Initialize database on import
init_db()
medicines, users, orders, cart = load_data()

# Ensure there is at least one admin user for admin login
if 'admin' not in users:
    users['admin'] = {'password': 'admin123', 'address': 'Admin Panel', 'is_admin': True}
    save_data(medicines, users, orders, cart)
else:
    users['admin']['is_admin'] = True
    save_data(medicines, users, orders, cart)