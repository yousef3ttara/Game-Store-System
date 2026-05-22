CREATE DATABASE ProjectDB;
GO

USE ProjectDB;
GO

-- ==========================================
-- DIMENSION TABLES
-- ==========================================

CREATE TABLE Categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL
);

CREATE TABLE Platforms (
    platform_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL
);

CREATE TABLE Games (
    game_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    category_id INT FOREIGN KEY REFERENCES Categories(category_id),
    platform_id INT FOREIGN KEY REFERENCES Platforms(platform_id),
    release_date DATE
);

-- ==========================================
-- USERS TABLE
-- ==========================================

CREATE TABLE Users (
    user_id   INT IDENTITY(1,1) PRIMARY KEY,
    username  NVARCHAR(100) NOT NULL UNIQUE,
    email     NVARCHAR(200) NOT NULL UNIQUE,
    password_hash NVARCHAR(256) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- ==========================================
-- FACT TABLES
-- ==========================================

CREATE TABLE Orders (
    order_id   INT IDENTITY(1,1) PRIMARY KEY,
    user_id    INT FOREIGN KEY REFERENCES Users(user_id) NULL,
    order_date DATETIME DEFAULT GETDATE(),
    total_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE Order_Items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT FOREIGN KEY REFERENCES Orders(order_id),
    game_id  INT FOREIGN KEY REFERENCES Games(game_id),
    quantity INT NOT NULL,
    price    DECIMAL(10, 2) NOT NULL
);