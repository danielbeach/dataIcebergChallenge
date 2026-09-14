-- Challenge 1: Establish the fleet baseline for a single partition-prunable day.
SELECT
    date,
    COUNT(*) AS active_drives,
    ROUND(SUM(capacity_bytes::HUGEINT) / 1e18, 2) AS raw_exabytes
FROM drivestats
WHERE date = DATE '2024-12-31'
GROUP BY date;
