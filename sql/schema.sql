CREATE DATABASE IF NOT EXISTS ecommerce_profit;

USE ecommerce_profit;


-- =========================================================
-- 1. SUPPLIERS
-- =========================================================

CREATE TABLE suppliers (
    supplier_id VARCHAR(10) PRIMARY KEY,
    supplier_name VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    rating DECIMAL(3,2),
    lead_time_days INT
);


-- =========================================================
-- 2. PRODUCTS
-- =========================================================

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(150),
    category VARCHAR(100),
    supplier_id VARCHAR(10),
    product_cost DECIMAL(12,2),
    selling_price DECIMAL(12,2),

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
);


-- =========================================================
-- 3. CUSTOMERS
-- =========================================================

CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    customer_name VARCHAR(150),
    email VARCHAR(150),
    city VARCHAR(100),
    state VARCHAR(100),
    registration_date DATE
);


-- =========================================================
-- 4. ORDERS
-- =========================================================

CREATE TABLE orders (
    order_id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10),
    product_id VARCHAR(10),
    order_date DATETIME,
    quantity INT,
    selling_price DECIMAL(12,2),
    discount_percent DECIMAL(5,2),
    discount_amount DECIMAL(12,2),
    net_amount DECIMAL(12,2),
    product_cost DECIMAL(12,2),
    shipping_cost DECIMAL(12,2),
    payment_fee DECIMAL(12,2),
    profit DECIMAL(12,2),
    profit_margin DECIMAL(8,2),
    profit_status VARCHAR(20),
    discount_category VARCHAR(30),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- =========================================================
-- 5. PAYMENTS
-- =========================================================

CREATE TABLE payments (
    payment_id VARCHAR(10) PRIMARY KEY,
    order_id VARCHAR(10),
    payment_date DATETIME,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    payment_amount DECIMAL(12,2),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- =========================================================
-- 6. INVENTORY
-- =========================================================

CREATE TABLE inventory (
    inventory_id VARCHAR(10) PRIMARY KEY,
    product_id VARCHAR(10),
    stock_quantity INT,
    reorder_level INT,
    last_restock_date DATE,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);


-- =========================================================
-- 7. SHIPPING
-- =========================================================

CREATE TABLE shipping (
    shipping_id VARCHAR(10) PRIMARY KEY,
    order_id VARCHAR(10),
    shipping_date DATETIME,
    delivery_date DATETIME,
    shipping_method VARCHAR(50),
    shipping_status VARCHAR(50),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);


-- =========================================================
-- 8. RETURNS
-- =========================================================

CREATE TABLE returns (
    return_id VARCHAR(10) PRIMARY KEY,
    order_id VARCHAR(10),
    product_id VARCHAR(10),
    return_date DATETIME,
    return_reason VARCHAR(150),
    refund_amount DECIMAL(12,2),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);