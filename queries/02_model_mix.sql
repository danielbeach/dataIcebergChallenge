-- Challenge 2: Which models make up the fleet on a chosen date?
SELECT
    model,
    COUNT(*) AS active_drives,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS fleet_percent
FROM drivestats
WHERE date = DATE '2024-12-31'
GROUP BY model
ORDER BY active_drives DESC
LIMIT 15;
