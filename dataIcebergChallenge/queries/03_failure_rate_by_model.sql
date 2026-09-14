-- Challenge 3: Compare annualized failure rates for well-represented models.
WITH model_year AS (
    SELECT
        model,
        COUNT(*) AS drive_days,
        COUNT(DISTINCT serial_number) AS distinct_drives,
        COUNT(DISTINCT CASE WHEN failure = 1 THEN serial_number END) AS failed_drives
    FROM drivestats
    WHERE date >= DATE '2024-01-01' AND date < DATE '2025-01-01'
    GROUP BY model
)
SELECT
    model,
    distinct_drives,
    failed_drives,
    ROUND(100.0 * failed_drives * 365.25 / drive_days, 3) AS annualized_failure_rate_pct
FROM model_year
WHERE drive_days >= 100000
ORDER BY annualized_failure_rate_pct DESC, failed_drives DESC
LIMIT 20;
