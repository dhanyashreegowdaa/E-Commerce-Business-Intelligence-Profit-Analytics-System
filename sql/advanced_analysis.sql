USE ecommerce_profit;


-- ============================================================
-- ADVANCED ANALYSIS QUERIES
-- ============================================================


-- 1. MONTHLY SALES, PROFIT AND ORDERS
-- ============================================================

SELECT
    DATE_FORMAT(o.order_date, '%Y-%m') AS month,
    COUNT(*) AS total_orders,
    SUM(o.quantity) AS total_quantity,
    ROUND(SUM(o.quantity * o.selling_price), 2) AS gross_sales,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS net_sales,
    ROUND(
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ), 2
    ) AS total_profit
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY month;


-- 2. CATEGORY-WISE SALES AND PROFIT
-- ============================================================

SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.quantity) AS total_quantity,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales,
    ROUND(
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ), 2
    ) AS total_profit
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_profit DESC;


-- 3. TOP 10 PRODUCTS BY PROFIT
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS units_sold,
    ROUND(
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ), 2
    ) AS total_profit
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_profit DESC
LIMIT 10;


-- 4. TOP 10 PRODUCTS BY SALES
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS units_sold,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_sales DESC
LIMIT 10;


-- 5. CUSTOMER-WISE PURCHASE ANALYSIS
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.quantity) AS total_items,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_spent
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.state
ORDER BY total_spent DESC;


-- 6. TOP 10 CUSTOMERS BY SPENDING
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.state
ORDER BY total_spending DESC
LIMIT 10;


-- 7. STATE-WISE SALES ANALYSIS
-- ============================================================

SELECT
    c.state,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.state
ORDER BY total_sales DESC;


-- 8. PAYMENT METHOD ANALYSIS
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS total_payments,
    ROUND(SUM(payment_amount), 2) AS total_amount,
    ROUND(AVG(payment_amount), 2) AS average_payment
FROM payments
GROUP BY payment_method
ORDER BY total_amount DESC;


-- 9. PAYMENT STATUS ANALYSIS
-- ============================================================

SELECT
    payment_status,
    COUNT(*) AS number_of_payments,
    ROUND(SUM(payment_amount), 2) AS total_amount
FROM payments
GROUP BY payment_status
ORDER BY number_of_payments DESC;


-- 10. SHIPPING PERFORMANCE
-- ============================================================

SELECT
    delivery_status,
    COUNT(*) AS total_shipments,
    ROUND(AVG(shipping_cost), 2) AS average_shipping_cost
FROM shipping
GROUP BY delivery_status
ORDER BY total_shipments DESC;


-- 11. DELIVERY DELAY ANALYSIS
-- ============================================================

SELECT
    s.order_id,
    s.warehouse,
    s.expected_delivery,
    s.actual_delivery,
    DATEDIFF(
        s.actual_delivery,
        s.expected_delivery
    ) AS delay_days,
    s.delivery_status
FROM shipping s
WHERE s.actual_delivery IS NOT NULL
ORDER BY delay_days DESC;


-- 12. WAREHOUSE-WISE SHIPPING ANALYSIS
-- ============================================================

SELECT
    warehouse,
    COUNT(*) AS total_shipments,
    ROUND(SUM(shipping_cost), 2) AS total_shipping_cost,
    ROUND(AVG(shipping_cost), 2) AS average_shipping_cost
FROM shipping
GROUP BY warehouse
ORDER BY total_shipping_cost DESC;


-- 13. RETURN ANALYSIS
-- ============================================================

SELECT
    return_reason,
    COUNT(*) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refund
FROM returns
GROUP BY return_reason
ORDER BY total_returns DESC;


-- 14. PRODUCT-WISE RETURN ANALYSIS
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(r.return_id) AS return_count,
    ROUND(SUM(r.refund_amount), 2) AS total_refund
FROM returns r
JOIN products p
    ON r.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY return_count DESC;


-- 15. INVENTORY ALERT
-- Products where stock is at or below reorder level
-- ============================================================

SELECT
    i.product_id,
    p.product_name,
    p.category,
    i.stock_quantity,
    i.reorder_level,
    i.last_restock_date
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
WHERE i.stock_quantity <= i.reorder_level
ORDER BY i.stock_quantity ASC;


-- 16. SUPPLIER PERFORMANCE
-- ============================================================

SELECT
    s.supplier_id,
    s.supplier_name,
    s.city,
    s.state,
    s.rating,
    s.lead_time_days,
    COUNT(p.product_id) AS number_of_products
FROM suppliers s
LEFT JOIN products p
    ON s.supplier_id = p.supplier_id
GROUP BY
    s.supplier_id,
    s.supplier_name,
    s.city,
    s.state,
    s.rating,
    s.lead_time_days
ORDER BY s.rating DESC, s.lead_time_days ASC;


-- 17. PRODUCT PROFIT MARGIN
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.product_cost,
    p.selling_price,
    ROUND(
        ((p.selling_price - p.product_cost)
        / p.selling_price) * 100,
        2
    ) AS profit_margin_percent
FROM products p
WHERE p.selling_price > 0
ORDER BY profit_margin_percent DESC;


-- 18. DISCOUNT ANALYSIS
-- ============================================================

SELECT
    ROUND(COALESCE(discount_percent, 0), 0) AS discount_percent,
    COUNT(*) AS number_of_orders,
    SUM(quantity) AS units_sold,
    ROUND(
        SUM(
            quantity * selling_price
            * (1 - COALESCE(discount_percent, 0) / 100)
        ), 2
    ) AS net_sales
FROM orders
GROUP BY ROUND(COALESCE(discount_percent, 0), 0)
ORDER BY discount_percent;


-- 19. HIGH VALUE ORDERS
-- ============================================================

SELECT
    o.order_id,
    c.customer_name,
    p.product_name,
    o.quantity,
    o.selling_price,
    o.discount_percent,
    ROUND(
        o.quantity * o.selling_price
        * (1 - COALESCE(o.discount_percent, 0) / 100),
        2
    ) AS order_value
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN products p
    ON o.product_id = p.product_id
ORDER BY order_value DESC
LIMIT 10;


-- 20. CUSTOMER RANKING USING WINDOW FUNCTION
-- ============================================================

SELECT
    customer_id,
    customer_name,
    total_spending,
    RANK() OVER (
        ORDER BY total_spending DESC
    ) AS customer_rank
FROM
(
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ) AS total_spending
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY
        c.customer_id,
        c.customer_name
) AS customer_sales
ORDER BY customer_rank;


-- 21. CATEGORY RANKING BY PROFIT
-- ============================================================

SELECT
    category,
    total_profit,
    RANK() OVER (
        ORDER BY total_profit DESC
    ) AS category_rank
FROM
(
    SELECT
        p.category,
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ) AS total_profit
    FROM orders o
    JOIN products p
        ON o.product_id = p.product_id
    GROUP BY p.category
) AS category_profit
ORDER BY category_rank;


-- 22. MONTHLY SALES RANKING
-- ============================================================

SELECT
    month,
    total_sales,
    RANK() OVER (
        ORDER BY total_sales DESC
    ) AS sales_rank
FROM
(
    SELECT
        DATE_FORMAT(o.order_date, '%Y-%m') AS month,
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ) AS total_sales
    FROM orders o
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
) AS monthly_sales
ORDER BY sales_rank;


-- 23. PRODUCTS WITH LOW STOCK AND HIGH SALES
-- ============================================================

SELECT
    i.product_id,
    p.product_name,
    p.category,
    i.stock_quantity,
    i.reorder_level,
    SUM(o.quantity) AS units_sold
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
LEFT JOIN orders o
    ON i.product_id = o.product_id
GROUP BY
    i.product_id,
    p.product_name,
    p.category,
    i.stock_quantity,
    i.reorder_level
HAVING i.stock_quantity <= i.reorder_level
ORDER BY units_sold DESC;


-- 24. SUPPLIERS WITH LOW RATING
-- ============================================================

SELECT
    supplier_id,
    supplier_name,
    city,
    state,
    rating,
    lead_time_days
FROM suppliers
WHERE rating < 3
ORDER BY rating ASC;


-- 25. CUSTOMERS WITH MORE THAN ONE ORDER
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
HAVING COUNT(o.order_id) > 1
ORDER BY total_orders DESC;


-- 26. AVERAGE ORDER VALUE
-- ============================================================

SELECT
    ROUND(
        AVG(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS average_order_value
FROM orders o;


-- 27. TOTAL BUSINESS SUMMARY
-- ============================================================

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.quantity) AS total_items_sold,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales,
    ROUND(
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ), 2
    ) AS total_profit
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;


-- 28. RETURN RATE BY PRODUCT
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT r.return_id) AS returns,
    ROUND(
        COUNT(DISTINCT r.return_id)
        / NULLIF(COUNT(DISTINCT o.order_id), 0) * 100,
        2
    ) AS return_rate_percent
FROM products p
LEFT JOIN orders o
    ON p.product_id = o.product_id
LEFT JOIN returns r
    ON p.product_id = r.product_id
GROUP BY
    p.product_id,
    p.product_name
ORDER BY return_rate_percent DESC;


-- 29. CUSTOMER PURCHASE FREQUENCY
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    MIN(o.order_date) AS first_order,
    MAX(o.order_date) AS latest_order
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY order_count DESC;


-- 30. BEST PRODUCTS BY PROFIT MARGIN
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.product_cost,
    p.selling_price,
    ROUND(
        ((p.selling_price - p.product_cost)
        / NULLIF(p.selling_price, 0)) * 100,
        2
    ) AS profit_margin
FROM products p
WHERE p.selling_price > 0
ORDER BY profit_margin DESC
LIMIT 10;