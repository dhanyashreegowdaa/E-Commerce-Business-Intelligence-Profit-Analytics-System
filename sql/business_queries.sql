USE ecommerce_profit;


-- ============================================================
-- BUSINESS ANALYSIS QUERIES
-- ============================================================


-- 1. TOTAL SALES
-- ============================================================

SELECT
    ROUND(
        SUM(
            quantity * selling_price
            * (1 - COALESCE(discount_percent, 0) / 100)
        ), 2
    ) AS total_sales
FROM orders;


-- 2. TOTAL NUMBER OF ORDERS
-- ============================================================

SELECT
    COUNT(*) AS total_orders
FROM orders;


-- 3. TOTAL QUANTITY SOLD
-- ============================================================

SELECT
    SUM(quantity) AS total_quantity_sold
FROM orders;


-- 4. AVERAGE ORDER VALUE
-- ============================================================

SELECT
    ROUND(
        AVG(
            quantity * selling_price
            * (1 - COALESCE(discount_percent, 0) / 100)
        ), 2
    ) AS average_order_value
FROM orders;


-- 5. TOTAL PROFIT
-- ============================================================

SELECT
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


-- 6. MOST PROFITABLE PRODUCT
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
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
LIMIT 1;


-- 7. BEST-SELLING PRODUCT BY QUANTITY
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS total_units_sold
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_units_sold DESC
LIMIT 1;


-- 8. HIGHEST SALES CATEGORY
-- ============================================================

SELECT
    p.category,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC
LIMIT 1;


-- 9. MOST VALUABLE CUSTOMER
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
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
ORDER BY total_spending DESC
LIMIT 1;


-- 10. CUSTOMERS WITH HIGHEST NUMBER OF ORDERS
-- ============================================================

SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY total_orders DESC
LIMIT 10;


-- 11. STATE WITH HIGHEST SALES
-- ============================================================

SELECT
    c.state,
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
ORDER BY total_sales DESC
LIMIT 1;


-- 12. CITY-WISE SALES
-- ============================================================

SELECT
    c.city,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(o.order_id) AS orders,
    ROUND(
        SUM(
            o.quantity * o.selling_price
            * (1 - COALESCE(o.discount_percent, 0) / 100)
        ), 2
    ) AS total_sales
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.city
ORDER BY total_sales DESC;


-- 13. PAYMENT METHOD MOST USED
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS number_of_payments,
    ROUND(SUM(payment_amount), 2) AS total_amount
FROM payments
GROUP BY payment_method
ORDER BY number_of_payments DESC
LIMIT 1;


-- 14. PAYMENT METHOD WITH HIGHEST REVENUE
-- ============================================================

SELECT
    payment_method,
    ROUND(SUM(payment_amount), 2) AS total_payment_amount
FROM payments
GROUP BY payment_method
ORDER BY total_payment_amount DESC
LIMIT 1;


-- 15. PAYMENT STATUS ANALYSIS
-- ============================================================

SELECT
    payment_status,
    COUNT(*) AS number_of_payments,
    ROUND(SUM(payment_amount), 2) AS total_amount
FROM payments
GROUP BY payment_status
ORDER BY total_amount DESC;


-- 16. TOTAL REFUNDS
-- ============================================================

SELECT
    COUNT(*) AS total_returns,
    ROUND(SUM(refund_amount), 2) AS total_refund_amount
FROM returns;


-- 17. MOST COMMON RETURN REASON
-- ============================================================

SELECT
    return_reason,
    COUNT(*) AS return_count
FROM returns
GROUP BY return_reason
ORDER BY return_count DESC
LIMIT 1;


-- 18. PRODUCT WITH MOST RETURNS
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    COUNT(r.return_id) AS return_count,
    ROUND(SUM(r.refund_amount), 2) AS total_refund
FROM returns r
JOIN products p
    ON r.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name
ORDER BY return_count DESC
LIMIT 1;


-- 19. TOTAL SHIPPING COST
-- ============================================================

SELECT
    ROUND(SUM(shipping_cost), 2) AS total_shipping_cost
FROM shipping;


-- 20. AVERAGE SHIPPING COST
-- ============================================================

SELECT
    ROUND(AVG(shipping_cost), 2) AS average_shipping_cost
FROM shipping;


-- 21. WAREHOUSE WITH HIGHEST SHIPPING COST
-- ============================================================

SELECT
    warehouse,
    COUNT(*) AS shipments,
    ROUND(SUM(shipping_cost), 2) AS total_shipping_cost
FROM shipping
GROUP BY warehouse
ORDER BY total_shipping_cost DESC
LIMIT 1;


-- 22. DELIVERY STATUS ANALYSIS
-- ============================================================

SELECT
    delivery_status,
    COUNT(*) AS number_of_shipments
FROM shipping
GROUP BY delivery_status
ORDER BY number_of_shipments DESC;


-- 23. DELAYED ORDERS
-- ============================================================

SELECT
    s.order_id,
    s.warehouse,
    s.expected_delivery,
    s.actual_delivery,
    DATEDIFF(
        s.actual_delivery,
        s.expected_delivery
    ) AS delay_days
FROM shipping s
WHERE s.actual_delivery IS NOT NULL
  AND s.actual_delivery > s.expected_delivery
ORDER BY delay_days DESC;


-- 24. PRODUCTS THAT NEED REORDERING
-- ============================================================

SELECT
    i.product_id,
    p.product_name,
    p.category,
    i.stock_quantity,
    i.reorder_level
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
WHERE i.stock_quantity <= i.reorder_level
ORDER BY i.stock_quantity ASC;


-- 25. PRODUCT WITH LOWEST STOCK
-- ============================================================

SELECT
    i.product_id,
    p.product_name,
    p.category,
    i.stock_quantity
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id
ORDER BY i.stock_quantity ASC
LIMIT 1;


-- 26. SUPPLIER WITH MOST PRODUCTS
-- ============================================================

SELECT
    s.supplier_id,
    s.supplier_name,
    COUNT(p.product_id) AS number_of_products
FROM suppliers s
LEFT JOIN products p
    ON s.supplier_id = p.supplier_id
GROUP BY
    s.supplier_id,
    s.supplier_name
ORDER BY number_of_products DESC
LIMIT 1;


-- 27. BEST-RATED SUPPLIERS
-- ============================================================

SELECT
    supplier_id,
    supplier_name,
    rating,
    lead_time_days
FROM suppliers
ORDER BY rating DESC, lead_time_days ASC
LIMIT 10;


-- 28. SUPPLIERS WITH LONG DELIVERY LEAD TIME
-- ============================================================

SELECT
    supplier_id,
    supplier_name,
    rating,
    lead_time_days
FROM suppliers
ORDER BY lead_time_days DESC;


-- 29. PRODUCTS WITH HIGH PROFIT MARGIN
-- ============================================================

SELECT
    product_id,
    product_name,
    category,
    product_cost,
    selling_price,
    ROUND(
        (
            (selling_price - product_cost)
            / NULLIF(selling_price, 0)
        ) * 100,
        2
    ) AS profit_margin_percent
FROM products
WHERE selling_price > 0
ORDER BY profit_margin_percent DESC;


-- 30. COMPLETE BUSINESS SUMMARY
-- ============================================================

SELECT
    (SELECT COUNT(*) FROM orders) AS total_orders,

    (SELECT SUM(quantity)
     FROM orders) AS total_quantity_sold,

    (SELECT ROUND(
        SUM(
            quantity * selling_price
            * (1 - COALESCE(discount_percent, 0) / 100)
        ), 2)
     FROM orders) AS total_sales,

    (SELECT ROUND(
        SUM(
            o.quantity *
            (
                o.selling_price
                * (1 - COALESCE(o.discount_percent, 0) / 100)
                - p.product_cost
            )
        ), 2)
     FROM orders o
     JOIN products p
       ON o.product_id = p.product_id) AS total_profit,

    (SELECT ROUND(SUM(refund_amount), 2)
     FROM returns) AS total_refunds,

    (SELECT ROUND(SUM(shipping_cost), 2)
     FROM shipping) AS total_shipping_cost;