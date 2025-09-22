from data_storage import medicines, users, orders, cart, save_data

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Add Medicine")
        print("2. Remove Medicine")
        print("3. View Orders")
        print("4. Update Order Status")
        print("5. View Medicine Stock")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == "1":
            med_name = input("Enter medicine name: ")
            # Check for duplicate medicine name
            if med_name in medicines:
                print("This medicine already exists! Please choose a different name.")
                continue
            try:
                price = float(input("Enter price (INR): "))
                stock = int(input("Enter stock: "))
                if price < 0 or stock < 0:
                    print("Price and stock must be non-negative!")
                    continue
                # Confirm addition
                confirm = input(f"Add {med_name} with price ₹{price} and stock {stock}? (yes/no): ").lower()
                if confirm == 'yes':
                    medicines[med_name] = {"price": price, "stock": stock}
                    save_data(medicines, users, orders, cart)
                    print(f"{med_name} added successfully!")
                else:
                    print("Addition cancelled.")
            except ValueError:
                print("Invalid price or stock! Please enter numeric values.")
        elif choice == "2":
            med_name = input("Enter medicine name to remove: ")
            if med_name in medicines:
                del medicines[med_name]
                save_data(medicines, users, orders, cart)
                print(f"{med_name} removed!")
            else:
                print("Medicine not found!")
        elif choice == "3":
            for oid, order in orders.items():
                print(f"Order ID: {oid}, User: {order['username']}, Items: {order['items']}, Status: {order['status']}")
        elif choice == "4":
            order_id = input("Enter order ID: ")
            if order_id in orders:
                status = input("Enter new status (Processing/Shipped/Delivered): ")
                if status in ["Processing", "Shipped", "Delivered"]:
                    orders[order_id]["status"] = status
                    save_data(medicines, users, orders, cart)
                    print("Status updated!")
                else:
                    print("Invalid status!")
            else:
                print("Order not found!")
        elif choice == "5":
            print("\n=== Medicine Stock ===")
            if not medicines:
                print("No medicines available!")
            else:
                for med, details in medicines.items():
                    print(f"Medicine: {med}, Price: ₹{details['price']}, Stock: {details['stock']}")
        elif choice == "6":
            break
        else:
            print("Invalid choice!")