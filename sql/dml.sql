-- ============================================================
-- VIMS — DML Script (Milestone 5)
-- Digital Voter Information & Management System
-- Authors: Suhaib Ahmad, Muhammad Rehan Khan
-- ============================================================

USE vims_db;

-- ============================================================
-- SECTION A: LOAD DATA FROM CSV FILES
-- ============================================================
-- NOTE: Place all CSV files in C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/
-- or adjust secure_file_priv path to match your system.
-- In MySQL Workbench run:  SHOW VARIABLES LIKE 'secure_file_priv';
-- to find the allowed import path.

-- Load order matters: parent tables before child tables.

-- 1. Users (no FK dependencies)
LOAD DATA INFILE '/var/lib/mysql-files/users.csv'
INTO TABLE Users
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(user_id, username, password_hash, role);

-- 2. PollingStations (no FK dependencies)
LOAD DATA INFILE '/var/lib/mysql-files/polling_stations.csv'
INTO TABLE PollingStations
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(station_id, name, location_code, city, capacity);

-- 3. Families (no FK dependencies)
LOAD DATA INFILE '/var/lib/mysql-files/families.csv'
INTO TABLE Families
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(family_id, head_name, permanent_address);

-- 4. Voters (depends on Families and PollingStations)
LOAD DATA INFILE '/var/lib/mysql-files/voters.csv'
INTO TABLE Voters
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(voter_id, cnic, full_name, age, gender, family_id, station_id);

-- 5. AuditLogs (depends on Users)
LOAD DATA INFILE '/var/lib/mysql-files/audit_logs.csv'
INTO TABLE AuditLogs
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(log_id, user_id, action, target_table, target_id, timestamp);


-- ============================================================
-- SECTION B: UPDATE OPERATION
-- ============================================================

-- B1: Update the capacity of a specific polling station
--     Scenario: Station PSH-001 has been expanded from 500 to 750 voters.
UPDATE PollingStations
SET    capacity = 750
WHERE  location_code = 'PSH-001';

-- Verify the update
SELECT station_id, name, location_code, capacity
FROM   PollingStations
WHERE  location_code = 'PSH-001';


-- B2: Update a voter's family assignment
--     Scenario: Voter with a specific CNIC moved to a different family (transferred household).
UPDATE Voters
SET    family_id = 5
WHERE  cnic = (SELECT cnic FROM Voters ORDER BY voter_id LIMIT 1);

-- (Use any valid CNIC from your voters.csv in actual execution)


-- ============================================================
-- SECTION C: DELETE OPERATION
-- ============================================================

-- C1: Delete a test/dummy admin account that was created during setup
--     Note: CASCADE will also remove their AuditLog entries.
DELETE FROM Users
WHERE  username = 'admin_test_dummy'
  AND  role = 'Administrator';

-- C2: Remove audit log entries older than a specific date
--     Scenario: Clearing out logs before system launch for a clean audit trail.
DELETE FROM AuditLogs
WHERE  timestamp < '2025-01-15 00:00:00';

-- ============================================================
-- END OF DML
-- ============================================================
