from data_storage import medicines, users, orders, cart, calculate_total_cost, generate_order_id, calculate_delivery_time, save_data
from getpass import getpass
from datetime import datetime, timedelta
import webbrowser
import os

def validate_password(password):
    return len(password) >= 6

def register():
    username = input("Enter username: ")
    if username in users:
        print("Username already exists!")
        return
    password = getpass("Enter password: ")
    if not validate_password(password):
        print("Password must be at least 6 characters!")
        return
    address = input("Enter delivery address: ")
    users[username] = {"password": password, "address": address}
    save_data(medicines, users, orders, cart)
    print("Registration successful!")

def login():
    username = input("Enter username: ")
    password = getpass("Enter password: ").strip()
    if username in users:
        stored_password = users[username].get("password")
        print(f"Debug: Username: '{username}', Stored password: '{stored_password}', Input password: '{password}'")
        if stored_password and stored_password.lower() == password.lower():
            print(f"Welcome, {username}!")
            return username
        else:
            print("Invalid password!")
    else:
        print("Username not found!")
    return None

def search_medicines():
    query = input("Enter medicine name to search: ").lower()
    found = False
    for med in medicines:
        if query in med.lower():
            details = medicines[med]
            inr_price = details['price']
            print(f"{med}: ₹{inr_price}")
            found = True
    if not found:
        print("No matching medicines found!")

def add_to_cart():
    medicine = input("Enter medicine name to add to cart (e.g., Paracetamol, Ibuprofen, Amoxicillin): ")
    if medicine not in medicines:
        print("Medicine not found!")
        return
    try:
        quantity = int(input("Enter quantity: "))
        if quantity <= 0:
            print("Quantity must be positive!")
            return
        if medicines[medicine]["stock"] < quantity:
            print(f"Only {medicines[medicine]['stock']} units available!")
            return
        cart[medicine] = cart.get(medicine, 0) + quantity
        save_data(medicines, users, orders, cart)
        print(f"{quantity} {medicine} added to cart for ₹{medicines[medicine]['price'] * quantity}!")
    except ValueError:
        print("Invalid quantity!")

def upload_prescription():
    prescription = input("Enter prescription details (e.g., doctor's name, medicine list): ")
    return prescription

def place_order(username):
    if not cart:
        print("Cart is empty!")
        return
    prescription = upload_prescription()
    order_id = generate_order_id()
    delivery_time = calculate_delivery_time()
    orders[order_id] = {
        "username": username,
        "items": cart.copy(),
        "prescription": prescription,
        "status": "Processing",
        "delivery_time": delivery_time
    }
    for med, qty in cart.items():
        medicines[med]["stock"] -= qty
    save_data(medicines, users, orders, cart)
    total_cost = calculate_total_cost(cart, medicines)
    print(f"Order placed! Order ID: {order_id}")
    print(f"Total Cost (including ₹417.5 delivery): ₹{total_cost}")
    print(f"Estimated Delivery: {delivery_time.strftime('%Y-%m-%d %H:%M:%S')}")
    cart.clear()

def cancel_order():
    order_id = input("Enter order ID to cancel: ")
    if order_id in orders:
        order = orders[order_id]
        if order["status"] == "Processing":
            time_limit = timedelta(minutes=30)
            current_time = datetime.now()
            delivery_time = order["delivery_time"]
            cutoff_time = delivery_time - time_limit
            
            if current_time < cutoff_time:
                del orders[order_id]
                save_data(medicines, users, orders, cart)
                print(f"Order {order_id} cancelled!")
            else:
                print("Too close to delivery time! Cancellation not allowed.")
        else:
            print("Order not found or cannot be cancelled (already shipped/delivered)!")
    else:
        print("Order not found!")

def date_of_arrival():
    order_id = input("Enter order ID: ")
    if order_id in orders:
        delivery_time = orders[order_id]["delivery_time"]
        print(f"Order ID: {order_id}")
        print(f"Date of Arrival: {delivery_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Order not found!")

def view_cart():
    # Display the contents of the user's cart
    if not cart:
        print("Your cart is empty!")
        return
    print("\n=== Your Cart ===")
    total = 0
    for medicine, quantity in cart.items():
        price = medicines[medicine]["price"]
        item_total = price * quantity
        total += item_total
        print(f"{medicine}: {quantity} x ₹{price} = ₹{item_total}")
    print(f"Subtotal (excluding delivery): ₹{total}")

def upload_prescription_photo():
    import webbrowser
    import subprocess
    import time
    import os
    
    # Start Flask server if not running
    try:
        import requests
        requests.get("http://127.0.0.1:5000/", timeout=2)
        print("Flask server is already running.")
    except:
        print("Starting Flask server...")
        # Start server in background
        subprocess.Popen([
            "python", "server.py"
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        time.sleep(3)  # Give server time to start
    
    webbrowser.open("http://127.0.0.1:5000/")
    print("Prescription upload page opened in your browser. Please scan and submit your prescription.")

