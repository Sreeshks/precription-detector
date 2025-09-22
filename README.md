# Online Medicine Delivery System

A comprehensive web-based medicine delivery platform with AI-powered prescription scanning using Gemini 2.0 Flash and Tesseract.js OCR.

## Features

### 🔐 User Authentication
- **Register**: Create new user accounts with username, password, and delivery address
- **Login**: Secure user authentication with session management
- **Logout**: Safe session termination

### 🔍 Medicine Search & Management
- **Search Medicines**: Real-time search through available medicine catalog
- **Browse Catalog**: View all available medicines with prices and stock information
- **Stock Management**: Real-time stock tracking and availability

### 🛒 Shopping Cart
- **Add to Cart**: Add medicines with custom quantities
- **View Cart**: Review selected items with pricing breakdown
- **Update Quantities**: Modify item quantities with stock validation
- **Remove Items**: Delete unwanted items from cart
- **Price Calculation**: Automatic subtotal and total calculation including delivery fees

### 📦 Order Management
- **Place Order**: Convert cart to order with prescription details
- **View Orders**: Track all user orders with status updates
- **Cancel Order**: Cancel orders within 30 minutes of delivery time
- **Date of Arrival**: View estimated delivery times
- **Order Status**: Track Processing → Shipped → Delivered status

### 📷 AI-Powered Prescription Upload
- **Image Upload**: Upload prescription photos (JPG, PNG, etc.)
- **OCR Processing**: Extract text using Tesseract.js
- **AI Medicine Detection**: Use Gemini 2.0 Flash for intelligent medicine recognition
- **Fuzzy Matching**: Advanced algorithms for medicine name matching
- **Auto Add to Cart**: Automatically add detected medicines to cart

## Technology Stack

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Custom properties, Grid, Flexbox, animations
- **JavaScript (ES6+)**: Async/await, Fetch API, DOM manipulation
- **Tesseract.js**: Client-side OCR processing

### Backend
- **Python Flask**: Web framework with session management
- **SQLite**: Database for persistent storage
- **Google Gemini 2.0 Flash**: AI-powered medicine detection
- **CORS Support**: Cross-origin resource sharing

### Database Schema
- **medicines**: name, price, stock
- **users**: username, password, address
- **orders**: order_id, username, items, prescription, status, delivery_time
- **cart**: medicine, quantity (session-based)

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```env
api_key=your_gemini_api_key_here
SECRET_KEY=your_flask_secret_key_here
```

### 3. Run the Application
```bash
python server.py
```

### 4. Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

## Usage Guide

### Getting Started
1. **Register** a new account or **Login** with existing credentials
2. **Browse** the medicine catalog or **Search** for specific medicines
3. **Add medicines** to your cart with desired quantities
4. **Review your cart** and proceed to place an order
5. **Upload prescription** if required
6. **Track your orders** and manage deliveries

### Prescription Upload Process
1. Navigate to the **"Upload Prescription"** tab
2. Click **"Choose file"** and select your prescription image
3. Click **"Scan Prescription"** to process the image
4. Review the **detected medicines** in the chips display
5. Click **"Add Detected to Cart"** to add all detected medicines
6. Switch to **Cart tab** to review and place your order

### Order Management
- **Place Order**: Requires prescription details and non-empty cart
- **Cancel Order**: Available only for "Processing" status orders
- **Delivery Time**: Calculated based on 3:00 PM IST cutoff
- **Order Status**: Automatically updated through the system

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration  
- `POST /logout` - User logout

### Medicine Catalog
- `GET /medicines` - Get all medicines
- `POST /extract_medicines` - AI medicine detection from text

### Cart Management
- `POST /add_to_cart` - Add medicine to cart
- `GET /get_cart` - Get user's cart
- `POST /update_cart` - Update cart quantities
- `POST /remove_from_cart` - Remove item from cart

### Order Management
- `POST /place_order` - Create new order
- `GET /get_orders` - Get user's orders
- `POST /cancel_order` - Cancel existing order

## File Structure
```
demo project/
├── server.py              # Flask web server
├── index.html             # Main web interface
├── main.py               # Command-line interface
├── user_operation.py     # User operations
├── admin_operation.py    # Admin operations
├── data_storage.py       # Database operations
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── delivery.db          # SQLite database
└── README.md            # This file
```

## Default Medicine Catalog
The system comes pre-loaded with common medicines:
- Paracetamol, Ibuprofen, Antacid, Cough Syrup
- Vitamin C, Allergy Relief, Metformin, Atorvastatin
- Chemotherapy Drug, Insulin, Livogon

## Security Features
- Password validation (minimum 6 characters)
- Session-based authentication
- CORS protection
- Input sanitization
- Stock validation
- Order cancellation time limits

## Troubleshooting

### Common Issues
1. **Server not starting**: Check if port 5000 is available
2. **AI detection not working**: Verify Gemini API key in `.env`
3. **Database errors**: Delete `delivery.db` to reset database
4. **CORS errors**: Ensure server is running on localhost:5000

### Error Messages
- "Flask server is not running": Start the server with `python server.py`
- "Medicines database not loaded": Check server connection
- "Insufficient stock": Medicine out of stock or quantity too high
- "Too close to delivery time": Order cancellation window expired

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is for educational and demonstration purposes.

## Support
For issues and questions, please check the troubleshooting section or create an issue in the repository.
