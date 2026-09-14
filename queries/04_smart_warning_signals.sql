-- Challenge 4: Do SMART attributes differ before a drive's recorded failure?
WITH failed_drives AS (
    SELECT serial_number, MIN(date) AS failure_date
    FROM drivestats
    WHERE failure = 1
    GROUP BY serial_number
)
SELECT
    d.model,
    COUNT(*) AS observations_30_days_before_failure,
    ROUND(AVG(d.smart_5_raw), 1) AS avg_reallocated_sectors,
    ROUND(AVG(d.smart_187_raw), 1) AS avg_reported_uncorrectable_errors,
    ROUND(AVG(d.smart_197_raw), 1) AS avg_pending_sectors
FROM drivestats AS d
JOIN failed_drives AS f USING (serial_number)
WHERE d.date >= f.failure_date - INTERVAL 30 DAY
  AND d.date < f.failure_date
GROUP BY d.model
HAVING COUNT(*) >= 100
ORDER BY avg_pending_sectors DESC NULLS LAST
LIMIT 20;
