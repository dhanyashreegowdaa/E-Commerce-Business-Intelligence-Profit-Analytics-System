-- Data Cleaning Queries
-- This file contains SQL queries for data validation and cleaning operations

-- 1. Remove duplicate orders
DELETE FROM orders
WHERE order_id IN (
    SELECT order_id
    FROM (
        SELECT order_id,
               ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY order_date) AS rn
        FROM orders
    ) AS subquery
    WHERE rn > 1
);

-- 2. Identify and handle NULL values in critical fields
SELECT 'customers' AS table_name, COUNT(*) AS null_count
FROM customers
WHERE customer_name IS NULL OR email IS NULL
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS null_count
FROM orders
WHERE customer_id IS NULL OR order_date IS NULL
UNION ALL
SELECT 'products' AS table_name, COUNT(*) AS null_count
FROM products
WHERE product_name IS NULL OR unit_price IS NULL;

-- 3. Identify invalid prices (negative or zero values)
SELECT product_id, product_name, unit_price, cost_price
FROM products
WHERE unit_price <= 0 OR cost_price <= 0;

-- 4. Identify inconsistent order amounts
SELECT o.order_id, o.order_amount, SUM(oi.quantity * oi.unit_price) AS calculated_amount
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_amount
HAVING o.order_amount <> SUM(oi.quantity * oi.unit_price);

-- 5. Identify orphaned records (orders without customers)
SELECT o.order_id, o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- 6. Standardize order status values
UPDATE orders
SET order_status = CASE
    WHEN order_status IN ('pending', 'PENDING', 'Pending') THEN 'Pending'
    WHEN order_status IN ('completed', 'COMPLETED', 'Completed') THEN 'Completed'
    WHEN order_status IN ('cancelled', 'CANCELLED', 'Cancelled') THEN 'Cancelled'
    ELSE order_status
END;

-- 7. Identify duplicate customers (by email)
SELECT email, COUNT(*) AS duplicate_count
FROM customers
WHERE email IS NOT NULL
GROUP BY email
HAVING COUNT(*) > 1;

-- 8. Identify orders with returns exceeding order amount
SELECT o.order_id, o.order_amount, r.return_amount
FROM orders o
JOIN returns r ON o.order_id = r.order_id
WHERE r.return_amount > o.order_amount;

-- 9. Validate date consistency (delivery date should be after shipping date)
SELECT s.shipping_id, s.shipping_date, s.delivery_date
FROM shipping s
WHERE s.delivery_date < s.shipping_date;

-- 10. Check for inventory inconsistencies
SELECT p.product_id, p.product_name, i.quantity_on_hand, i.reorder_level
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand < 0;
