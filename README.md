<div align="center">
  <img src="game_store_detailed_thumbnail.png" alt="Game Store System Banner" width="100%">
</div>

# 🎮 Game Store System - Full-Stack E-Commerce App

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## 📌 Project Overview
The **Game Store System** is a comprehensive full-stack web application designed to simulate a digital video game storefront. It provides a seamless and interactive interface for users to browse a catalog of games, manage their shopping carts, and securely complete purchases. The system features an automated inventory management backend that dynamically updates stock quantities upon successful transactions, ensuring data consistency and accuracy.

## ✨ Core Features
* **User Authentication:** Secure registration and login system with session management and SHA-256 password hashing.
* **Dynamic Game Catalog:** Browse available games, viewing real-time details such as price, genre, platform, available stock, and release date.
* **Interactive Shopping Cart:** A smooth cart management system allowing users to adjust quantities and calculate total prices before checkout.
* **Automated Inventory Management:** Once an order is successfully placed, the backend automatically deducts the purchased quantities from the database, preventing overselling.
* **Order History Tracking:** Users can view their personal order history, while administrators can track all past orders, including transaction dates and line-item details.
* **Asynchronous Operations:** The frontend utilizes AJAX/Fetch requests to communicate with the RESTful API, providing a fast, single-page-like experience without full page reloads.

## 🛠️ Technologies Used
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python 3, Flask micro-framework
* **Database:** Microsoft SQL Server
* **Data Connectivity:** `pyodbc`, RESTful architecture

## 💡 Database Architecture
The database is highly optimized and normalized, utilizing Data Warehousing concepts to separate descriptive details from transactional records:

**Dimension Tables (Lookup Tables):**
- `Users`: Stores user accounts, credentials (hashed), and emails.
- `Categories`: Descriptive attributes about game genres.
- `Platforms`: Descriptive attributes about gaming systems.
- `Games`: The product dimension, containing details like name, price, and release date.

**Fact Tables (Transaction Tables):**
- `Orders`: Records the occurrence of a purchase event (Total Price, Date, User ID).
- `Order_Items`: Granular line-item metrics (quantity, price) linked to specific games and orders.

## 🔌 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Registers a new user and starts a session. |
| `POST` | `/login` | Authenticates a user and starts a session. |
| `POST` | `/logout` | Clears the current user session. |
| `GET`  | `/me` | Retrieves information about the currently logged-in user. |
| `GET`  | `/games` | Retrieves a list of all available games in the store. |
| `POST` | `/buy`   | Processes a purchase, updates inventory, and creates an order record linked to the user. |
| `GET`  | `/orders`| Retrieves a complete list of all past orders. |
| `GET`  | `/my-orders`| Retrieves a list of past orders specific to the logged-in user. |

## 🚀 How to Run the Project

### 1. Database Setup
1. Install Microsoft SQL Server and SQL Server Management Studio (SSMS).
2. Open `setup_nexusdb.sql` in SSMS and execute it (Press F5) to create the database schema (`NexusDB`), tables, and seed the initial data.
3. (Optional) To import games directly from the CSV file, you can run `bulk_insert_games.sql` instead of the manual inserts, or use the SSMS Import Flat File Wizard on `data.csv`.

### 2. Backend Setup
1. Ensure **Python 3.x** is installed on your system.
2. Open a terminal and navigate to the project directory.
3. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
4. Install the required Python dependencies:
   ```bash
   pip install flask flask-cors pyodbc
   ```
5. Open `app.py` and update the database connection string to match your local SQL Server credentials (Server Name):
   ```python
   conn = pyodbc.connect(
       "DRIVER={SQL Server};SERVER=YOUR_SERVER_NAME;DATABASE=NexusDB;Trusted_Connection=yes;"
   )
   ```
6. Start the Flask server:
   ```bash
   python app.py
   ```
   *The API will start running on `http://localhost:5000`.*

### 3. Frontend Setup
1. The Flask app is configured to serve the HTML files directly for your convenience.
2. Navigate to `http://localhost:5000/` in your web browser to view the game store.
3. Access the orders tracking page via `http://localhost:5000/orders-page`.

---
<div align="center">
  <i>Developed with ❤️ for building robust, full-stack data solutions.</i>
</div>
