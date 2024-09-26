SELECT table_schema || '.' || table_name AS table_full_name,
    row_estimate AS estimated_rows
FROM (
        SELECT schemaname AS table_schema,
            relname AS table_name,
            n_live_tup AS row_estimate
        FROM pg_stat_user_tables
    ) AS row_counts
ORDER BY row_estimate DESC;