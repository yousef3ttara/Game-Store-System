# Game Store System - Project Report

## 1. Project Title
**Game Store System** - A Full-Stack Web Application for Game Management and Purchasing.

## 2. Project Overview

### Idea
The Game Store System is a comprehensive web-based platform designed to simulate an online digital or physical video game storefront. It provides a seamless interface for users to browse a catalog of games, manage their shopping carts, and complete purchases while tracking order history.

### Problem
Managing inventory, processing transactions, and providing a user-friendly storefront can be challenging for game retailers. Manual tracking of stock quantities often leads to discrepancies, and customers require an intuitive way to filter, view, and purchase games across various platforms and categories.

### Solution
This project solves these issues by providing an automated, centralized full-stack application. It integrates a responsive frontend with a robust backend API and a relational database to manage inventory automatically. When a purchase is made, the stock is dynamically updated, ensuring consistency and accuracy in the digital storefront.

### Objectives
- Develop a user-friendly frontend for browsing games and placing orders.
- Implement secure user authentication with session management.
- Create a RESTful API to bridge the frontend and the database efficiently.
- Design a normalized relational database to securely store users, games, categories, platforms, and order data.
- Automate stock management upon successful transactions.
- Provide a clear view of transaction histories for administrative or individual user tracking.

## 3. System Architecture

### Frontend
The presentation layer is built using standard web technologies: **HTML**, **CSS**, and **JavaScript**. It communicates asynchronously with the backend API to render game lists, manage the shopping cart, and process checkout operations without requiring full page reloads.

### Backend
The application logic is powered by a **Python Flask API**. It handles HTTP requests from the frontend, executes business logic (such as calculating totals and validating stock), interacts with the database, and returns data in JSON format.

### Database
The data layer utilizes **SQL Server**, a robust relational database management system. It ensures data integrity and supports complex queries required for retrieving games, filtering by categories/platforms, and maintaining transactional records.

### Data Flow
1. **Client Request**: The user interacts with the UI (e.g., viewing games, clicking "Buy"). The frontend JavaScript sends an HTTP request (GET/POST) to the Flask API.
2. **Backend Processing**: The Flask application parses the request, formulates the appropriate SQL query, and connects to the SQL Server database.
3. **Database Execution**: SQL Server executes the query, retrieving or updating records (e.g., deducting stock_quantity) and returns the result to the API.
4. **Response**: The Flask API formats the data as a JSON response and sends it back to the client, which updates the UI accordingly.

## 4. Database Schema

### Tables
| Table | Columns |
|-------|---------|
| **Users** | `user_id`, `username`, `email`, `password_hash`, `created_at` |
| **Games** | `game_id`, `name`, `price`, `stock_quantity`, `category_id`, `platform_id`, `release_date` |
| **Categories** | `category_id`, `name` |
| **Platforms** | `platform_id`, `name` |
| **Orders** | `order_id`, `user_id`, `order_date`, `total_price` |
| **Order_Items** | `id`, `order_id`, `game_id`, `quantity`, `price` |

### Relationships Explanation
- **Users to Orders (One-to-Many):** A single user can place multiple orders. The `user_id` in the `Orders` table acts as a foreign key linking back to the specific user in the `Users` table (can be NULL for guest checkouts).
- **Games to Categories (Many-to-One):** Each game belongs to a specific category (e.g., Action, RPG). The `category_id` in the `Games` table is a foreign key referencing `category_id` in the `Categories` table.
- **Games to Platforms (Many-to-One):** Each game is associated with a specific platform (e.g., PC, PlayStation). The `platform_id` in the `Games` table is a foreign key referencing `platform_id` in the `Platforms` table.
- **Orders to Order_Items (One-to-Many):** A single order can contain multiple games. The `order_id` in the `Order_Items` table acts as a foreign key linking back to the specific order in the `Orders` table.
- **Games to Order_Items (One-to-Many):** A specific game can be part of many different orders over time. The `game_id` in the `Order_Items` table is a foreign key referencing the `game_id` in the `Games` table.

### Fact vs Dimension Tables (Data Warehousing Concepts)
In the context of data analysis and star-schema design, the tables in this system can be categorized as follows:

**Dimension Tables (Lookup Tables):**
- **Users**: Stores user accounts, hashed credentials, and emails.
- **Categories**: Stores descriptive attributes about the game genres.
- **Platforms**: Stores descriptive attributes about the systems games run on.
- **Games**: Acts as a product dimension, containing descriptive and qualitative data (name, release_date) about the items sold.

**Fact Tables (Transaction Tables):**
- **Orders**: A transaction fact table recording the occurrence of a purchase event (order_date, total_price).
- **Order_Items**: A line-item fact table recording the granular metrics of the transaction (quantity, price) linked to specific dimension keys (game_id).

## 5. API Documentation

### Endpoints

#### `POST /register`
- **Description**: Registers a new user with a username, email, and password, hashing the password using SHA-256 and initiating a session.

#### `POST /login`
- **Description**: Authenticates a user with a username or email and password, starting a secure session.

#### `POST /logout`
- **Description**: Clears the current user's active session.

#### `GET /me`
- **Description**: Retrieves session data for the currently logged-in user.

#### `GET /games`
- **Description**: Retrieves a list of all available games in the store.
- **Request Parameters**: None
- **Response Example**:
  ```json
  [
    {
      "game_id": 1,
      "name": "Cyberpunk 2077",
      "price": 59.99,
      "stock_quantity": 45,
      "category_id": 2,
      "platform_id": 1,
      "release_date": "2020-12-10"
    }
  ]
  ```

#### `POST /buy`
- **Description**: Processes a purchase, creates a new order, records order items, and deducts the purchased quantities from the game stock.
- **Request Example**:
  ```json
  {
    "items": [
      {
        "game_id": 1,
        "quantity": 2
      },
      {
        "game_id": 3,
        "quantity": 1
      }
    ]
  }
  ```
- **Response Example**:
  ```json
  {
    "message": "Order placed successfully",
    "order_id": 101,
    "total_price": 179.97
  }
  ```

#### `GET /orders`
- **Description**: Retrieves a complete list of past orders including their total prices and dates for all users.
- **Request Parameters**: None
- **Response Example**:
  ```json
  [
    {
      "order_id": 101,
      "order_date": "2023-10-25T14:30:00",
      "total_price": 179.97
    }
  ]
  ```

#### `GET /my-orders`
- **Description**: Retrieves a list of past orders specific to the currently logged-in user session.

## 6. Features
- **User Authentication**: Secure registration and login functionalities using session management and password hashing.
- **Browse Games**: Users can view a complete catalog of available games including their prices, platforms, and current stock.
- **Shopping Cart**: Users can select games and add them to a virtual cart before purchasing.
- **Checkout Processing**: Secure calculation of total prices and generation of order records linked to the authenticated user.
- **Automated Inventory Management**: The system automatically subtracts the purchased quantity from the `stock_quantity` of a game once an order is placed.
- **Order History**: Users can securely view their personal order history, while administrators can track all historical orders.

## 7. Technologies Used
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python, Flask (Web Framework)
- **Database**: Microsoft SQL Server
- **Data Exchange**: JSON, RESTful architecture

## 8. Future Improvements
- **Admin Dashboard**: Create a dedicated interface for store owners to add, update, or remove games and categories.
- **Payment Gateway Integration**: Integrate third-party payment processors like Stripe or PayPal for real transactions.
- **Advanced Filtering and Search**: Add capabilities to search for games by name or filter by specific categories, platforms, or price ranges.
- **Pagination**: Implement pagination on the `/games` and `/orders` endpoints to handle large datasets efficiently.

## 9. How to Run the Project
1. **Database Setup**:
   - Install Microsoft SQL Server and SQL Server Management Studio (SSMS).
   - Execute the `setup_nexusdb.sql` script in SSMS (Press F5) to create the database (`NexusDB`), the required tables (including Users and Orders), and to insert initial seed data (Games, Categories, Platforms).
   - Alternatively, you can run `bulk_insert_games.sql` or use SSMS Import Wizard to import games directly from `data.csv`.
2. **Backend Setup**:
   - Ensure Python 3.x is installed.
   - Navigate to the backend directory and create a virtual environment: `python -m venv venv`
   - Activate the virtual environment and install dependencies: `pip install flask pyodbc`
   - Update the database connection string in `app.py` to match your SQL Server credentials.
   - Run the Flask server: `python app.py` (The API will typically run on `http://localhost:5000`).
3. **Frontend Setup**:
   - Open the `index.html` file in any modern web browser.
   - Ensure the JavaScript file is correctly pointing to the local Flask API endpoints.

## 10. Conclusion
The Game Store System successfully demonstrates a complete end-to-end full-stack web application. By effectively separating concerns across the frontend, backend, and database layers, the project highlights fundamental concepts in web development, API design, and relational database management. The resulting system is scalable, easily maintainable, and provides a solid foundation for more advanced e-commerce features.
