-- ============================================================
-- VIMS — Validation Queries (Milestone 5)
-- Run these after data population and screenshot each output.
-- ============================================================

USE vims_db;

-- ============================================================
-- 1. ROW COUNT VALIDATION — COUNT(*) for every table
-- ============================================================

SELECT 'Users'           AS table_name, COUNT(*) AS row_count FROM Users
UNION ALL
SELECT 'PollingStations' AS table_name, COUNT(*) AS row_count FROM PollingStations
UNION ALL
SELECT 'Families'        AS table_name, COUNT(*) AS row_count FROM Families
UNION ALL
SELECT 'Voters'          AS table_name, COUNT(*) AS row_count FROM Voters
UNION ALL
SELECT 'AuditLogs'       AS table_name, COUNT(*) AS row_count FROM AuditLogs;

-- Expected: 15, 20, 80, 150, 100 (or similar based on your CSV)


-- ============================================================
-- 2. NULL CHECK — Key columns must not have NULL values
-- ============================================================

-- Voters: cnic, full_name, age, gender, station_id must never be NULL
SELECT 'Voters - NULL cnic'      AS check_name, COUNT(*) AS null_count FROM Voters WHERE cnic IS NULL
UNION ALL
SELECT 'Voters - NULL full_name' AS check_name, COUNT(*) AS null_count FROM Voters WHERE full_name IS NULL
UNION ALL
SELECT 'Voters - NULL age'       AS check_name, COUNT(*) AS null_count FROM Voters WHERE age IS NULL
UNION ALL
SELECT 'Voters - NULL gender'    AS check_name, COUNT(*) AS null_count FROM Voters WHERE gender IS NULL
UNION ALL
SELECT 'Voters - NULL station_id'AS check_name, COUNT(*) AS null_count FROM Voters WHERE station_id IS NULL;

-- Users: username, password_hash, role must never be NULL
SELECT 'Users - NULL username'      AS check_name, COUNT(*) AS null_count FROM Users WHERE username IS NULL
UNION ALL
SELECT 'Users - NULL password_hash' AS check_name, COUNT(*) AS null_count FROM Users WHERE password_hash IS NULL
UNION ALL
SELECT 'Users - NULL role'          AS check_name, COUNT(*) AS null_count FROM Users WHERE role IS NULL;

-- AuditLogs: user_id, action, target_table, target_id, timestamp must never be NULL
SELECT 'AuditLogs - NULL user_id'      AS check_name, COUNT(*) AS null_count FROM AuditLogs WHERE user_id IS NULL
UNION ALL
SELECT 'AuditLogs - NULL action'       AS check_name, COUNT(*) AS null_count FROM AuditLogs WHERE action IS NULL
UNION ALL
SELECT 'AuditLogs - NULL target_table' AS check_name, COUNT(*) AS null_count FROM AuditLogs WHERE target_table IS NULL
UNION ALL
SELECT 'AuditLogs - NULL timestamp'    AS check_name, COUNT(*) AS null_count FROM AuditLogs WHERE timestamp IS NULL;

-- Expected: All null_count values = 0


-- ============================================================
-- 3. FOREIGN KEY INTEGRITY — JOIN-based checks
-- ============================================================

-- 3a. Voters → Families: Find voters whose family_id has no matching family
SELECT v.voter_id, v.full_name, v.family_id
FROM   Voters v
LEFT JOIN Families f ON v.family_id = f.family_id
WHERE  v.family_id IS NOT NULL   -- NULL family_id is allowed (SET NULL on delete)
  AND  f.family_id IS NULL;      -- but non-NULL must exist
-- Expected: 0 rows (no orphaned family references)

-- 3b. Voters → PollingStations: Find voters whose station_id has no matching station
SELECT v.voter_id, v.full_name, v.station_id
FROM   Voters v
LEFT JOIN PollingStations ps ON v.station_id = ps.station_id
WHERE  ps.station_id IS NULL;
-- Expected: 0 rows

-- 3c. AuditLogs → Users: Find audit logs whose user_id has no matching user
SELECT al.log_id, al.user_id, al.action
FROM   AuditLogs al
LEFT JOIN Users u ON al.user_id = u.user_id
WHERE  u.user_id IS NULL;
-- Expected: 0 rows


-- ============================================================
-- 4. BUSINESS LOGIC VALIDATION
-- ============================================================

-- 4a. All voters must be 18 or older
SELECT voter_id, full_name, age
FROM   Voters
WHERE  age < 18;
-- Expected: 0 rows

-- 4b. CNIC uniqueness — no duplicate CNICs
SELECT cnic, COUNT(*) AS occurrences
FROM   Voters
GROUP BY cnic
HAVING COUNT(*) > 1;
-- Expected: 0 rows

-- 4c. Station capacity check — how many stations are over capacity?
SELECT ps.station_id, ps.name, ps.capacity,
       COUNT(v.voter_id) AS assigned_voters,
       (COUNT(v.voter_id) - ps.capacity) AS overflow
FROM   PollingStations ps
LEFT JOIN Voters v ON ps.station_id = v.station_id
GROUP BY ps.station_id, ps.name, ps.capacity
HAVING COUNT(v.voter_id) > ps.capacity;
-- Informational: shows stations exceeding capacity (if any)


-- ============================================================
-- 5. USEFUL JOIN QUERIES (for report / dashboard)
-- ============================================================

-- 5a. Full voter list with family and station details
SELECT v.voter_id, v.cnic, v.full_name, v.age, v.gender,
       f.head_name          AS family_head,
       f.permanent_address  AS address,
       ps.name              AS station_name,
       ps.city
FROM   Voters v
LEFT JOIN Families       f  ON v.family_id  = f.family_id
LEFT JOIN PollingStations ps ON v.station_id = ps.station_id
ORDER BY v.voter_id
LIMIT 20;

-- 5b. Voter count per polling station
SELECT ps.station_id, ps.name, ps.city, ps.capacity,
       COUNT(v.voter_id) AS total_voters,
       ROUND(COUNT(v.voter_id) * 100.0 / ps.capacity, 1) AS load_pct
FROM   PollingStations ps
LEFT JOIN Voters v ON ps.station_id = v.station_id
GROUP BY ps.station_id, ps.name, ps.city, ps.capacity
ORDER BY load_pct DESC;

-- 5c. Audit log with admin username
SELECT al.log_id, u.username, al.action,
       al.target_table, al.target_id, al.timestamp
FROM   AuditLogs al
JOIN   Users u ON al.user_id = u.user_id
ORDER BY al.timestamp DESC
LIMIT 20;

-- 5d. Gender distribution of voters
SELECT gender, COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Voters), 1) AS percentage
FROM   Voters
GROUP BY gender;

-- ============================================================
-- END OF VALIDATION QUERIES
-- ============================================================
