-- Challenge 5: Track fleet capacity and the mix of high-capacity drives over time.
WITH month_end AS (
    SELECT MAX(date) AS month_end_date
    FROM drivestats
    GROUP BY date_trunc('month', date)
),
snapshots AS (
    SELECT d.*
    FROM drivestats AS d
    JOIN month_end AS m ON d.date = m.month_end_date
)
SELECT
    date,
    COUNT(*) AS active_drives,
    ROUND(SUM(capacity_bytes::HUGEINT) / 1e18, 2) AS raw_exabytes,
    ROUND(100.0 * AVG(CASE WHEN capacity_bytes >= 16e12 THEN 1 ELSE 0 END), 2)
        AS drives_at_least_16tb_pct
FROM snapshots
GROUP BY date
ORDER BY date;
