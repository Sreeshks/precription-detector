from user_operation import register, login, add_to_cart, place_order, date_of_arrival, search_medicines, cancel_order, view_cart, upload_prescription_photo
from admin_operation import admin_menu
from getpass import getpass
from data_storage import save_data, medicines, users, orders, cart, init_db
import webbrowser

def main():
    # Initialize the database on program start
    init_db()
    
    while True:
        print("\nOnline Drug Delivery System")
        print("1. Register")
        print("2. Login")
        print("3. Admin Login")
        print("4. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            username = login()
            if username:
                while True:
                    print("\nUser Menu:")
                    print("1. Search Medicines")
                    print("2. Add to Cart")
                    print("3. Place Order")
                    print("4. Cancel Order")
                    print("5. Date of Arrival")
                    print("6. Logout")
                    print("7. View Cart")
                    print("8. Upload Prescription Photo")
                    try:
                        user_choice = int(input("Enter choice: "))
                        if user_choice == 1:
                            search_medicines()
                        elif user_choice == 2:
                            add_to_cart()
                        elif user_choice == 3:
                            place_order(username)
                        elif user_choice == 4:
                            cancel_order()
                        elif user_choice == 5:
                            date_of_arrival()
                        elif user_choice == 6:
                            save_data(medicines, users, orders, cart)
                            break
                        elif user_choice == 7:
                            view_cart()
                        elif user_choice == 8:
                            upload_prescription_photo()
                        else:
                            print("Invalid choice! Please enter a number between 1 and 8.")
                    except ValueError:
                        print("Please enter a valid number (1-8)!")
        elif choice == "3":
            if getpass("Enter admin password: ") == "admin123":
                admin_menu()
            else:
                print("Invalid admin password!")
        elif choice == "4":
            save_data(medicines, users, orders, cart)
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()