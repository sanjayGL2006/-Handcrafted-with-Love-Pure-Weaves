-- ============================================================
--  Pure Weaves - MySQL Database Setup
--  File: database.sql
--  Run this file in MySQL Workbench or phpMyAdmin
-- ============================================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS pureweaves_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE pureweaves_db;

-- Step 2: Users table
CREATE TABLE IF NOT EXISTS users (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  mobile         VARCHAR(15) UNIQUE,
  email          VARCHAR(120) UNIQUE,
  google_id      VARCHAR(200) UNIQUE,
  is_admin       BOOLEAN DEFAULT FALSE,
  is_active      BOOLEAN DEFAULT TRUE,
  login_attempts INT DEFAULT 0,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Products table
CREATE TABLE IF NOT EXISTS products (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(200) NOT NULL,
  category    VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  price_min   DECIMAL(10,2) NOT NULL,
  price_max   DECIMAL(10,2) NOT NULL,
  image_path  VARCHAR(500),
  is_active   BOOLEAN DEFAULT TRUE,
  stock       INT DEFAULT 100,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Step 5: Cart table
CREATE TABLE IF NOT EXISTS cart_items (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  product_id INT NOT NULL,
  quantity   INT DEFAULT 1,
  added_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Step 6: Orders table
CREATE TABLE IF NOT EXISTS orders (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  total_amount  DECIMAL(10,2) NOT NULL,
  coupon_code   VARCHAR(50),
  discount      DECIMAL(10,2) DEFAULT 0,
  status        VARCHAR(50) DEFAULT 'pending',
  whatsapp_sent BOOLEAN DEFAULT FALSE,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Step 7: Order items table
CREATE TABLE IF NOT EXISTS order_items (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  order_id   INT NOT NULL,
  product_id INT NOT NULL,
  quantity   INT NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Step 8: Coupons table
CREATE TABLE IF NOT EXISTS coupons (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  code             VARCHAR(50) UNIQUE NOT NULL,
  discount_percent DECIMAL(5,2) NOT NULL,
  max_uses         INT DEFAULT 100,
  used_count       INT DEFAULT 0,
  expires_at       DATETIME NOT NULL,
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Step 9: Insert admin user (Pure Weaves owner)
INSERT IGNORE INTO users (name, mobile, is_admin) VALUES
  ('Pure Weaves Admin', '8088744654', TRUE);

-- Step 10: Insert sample coupons
INSERT IGNORE INTO coupons (code, discount_percent, max_uses, expires_at) VALUES
  ('WELCOME10', 10.00, 500, '2026-12-31'),
  ('FESTIVAL20', 20.00, 100, '2026-10-31'),
  ('BULK15', 15.00, 50, '2026-12-31');

-- ✅ Database setup complete!
-- Run: mysql -u root -p < database.sql
