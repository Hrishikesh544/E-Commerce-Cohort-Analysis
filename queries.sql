-- ====================================================================
-- PROJECT: E-Commerce Cohort Analysis
-- PURPOSE: Extract unified relational view of customer spending
-- DIALECT: SQLite
-- ====================================================================

-- 1. Master Extraction Query (Used in Python Pipeline)
SELECT 
    o.order_id,
    o.order_date,
    u.user_id,
    u.city,
    p.category,
    p.price
FROM orders o
JOIN users u 
    ON o.user_id = u.user_id
JOIN products p 
    ON o.product_id = p.product_id;

-- ====================================================================
-- BONUS ANALYTICS QUERIES (For future dashboarding)
-- ====================================================================

-- 2. Total Revenue and Order Count per City
SELECT 
    u.city,
    COUNT(o.order_id) AS total_orders,
    SUM(p.price) AS total_revenue
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id
GROUP BY u.city
ORDER BY total_revenue DESC;