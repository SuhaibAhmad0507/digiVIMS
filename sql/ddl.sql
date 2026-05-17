-- ============================================================
-- VIMS — DDL Script (Milestone 4)
-- Digital Voter Information & Management System
-- Authors: Suhaib Ahmad, Muhammad Rehan Khan
-- Course:  Database Systems Lab, IMSciences
-- ============================================================

DROP DATABASE IF EXISTS vims_db;
CREATE DATABASE vims_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE vims_db;

-- ------------------------------------------------------------
-- TABLE: Users
-- Stores system login credentials and role assignments.
-- ------------------------------------------------------------
CREATE TABLE Users (
    user_id       INT            NOT NULL AUTO_INCREMENT,
    username      VARCHAR(50)    NOT NULL,
    password_hash VARCHAR(255)   NOT NULL,
    role          ENUM('Administrator', 'Viewer') NOT NULL,

    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_username UNIQUE (username)
);

-- Index on role for role-based filtering queries
CREATE INDEX idx_users_role ON Users (role);


-- ------------------------------------------------------------
-- TABLE: PollingStations
-- Represents individual polling stations across cities.
-- ------------------------------------------------------------
CREATE TABLE PollingStations (
    station_id    INT            NOT NULL AUTO_INCREMENT,
    name          VARCHAR(100)   NOT NULL,
    location_code VARCHAR(20)    NOT NULL,
    city          VARCHAR(50)    NOT NULL,
    capacity      INT            NOT NULL CHECK (capacity > 0),

    CONSTRAINT pk_polling_stations PRIMARY KEY (station_id),
    CONSTRAINT uq_location_code    UNIQUE (location_code)
);

-- Index on city for station-wise city filtering
CREATE INDEX idx_stations_city ON PollingStations (city);


-- ------------------------------------------------------------
-- TABLE: Families
-- Represents Gharana (family) units grouping multiple voters.
-- ------------------------------------------------------------
CREATE TABLE Families (
    family_id         INT           NOT NULL AUTO_INCREMENT,
    head_name         VARCHAR(100)  NOT NULL,
    permanent_address TEXT          NOT NULL,

    CONSTRAINT pk_families PRIMARY KEY (family_id)
);

-- Index on head_name for family search by head
CREATE INDEX idx_families_head_name ON Families (head_name);


-- ------------------------------------------------------------
-- TABLE: Voters
-- Central table — individual voter records.
-- ------------------------------------------------------------
CREATE TABLE Voters (
    voter_id   INT           NOT NULL AUTO_INCREMENT,
    cnic       CHAR(15)      NOT NULL,
    full_name  VARCHAR(100)  NOT NULL,
    age        TINYINT       NOT NULL CHECK (age >= 18),
    gender     ENUM('Male', 'Female', 'Other') NOT NULL,
    family_id  INT,
    station_id INT           NOT NULL,

    CONSTRAINT pk_voters          PRIMARY KEY (voter_id),
    CONSTRAINT uq_voters_cnic     UNIQUE (cnic),
    CONSTRAINT fk_voters_family   FOREIGN KEY (family_id)
        REFERENCES Families(family_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_voters_station  FOREIGN KEY (station_id)
        REFERENCES PollingStations(station_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Indexes on foreign keys and frequently queried columns
CREATE INDEX idx_voters_family_id   ON Voters (family_id);
CREATE INDEX idx_voters_station_id  ON Voters (station_id);
CREATE INDEX idx_voters_full_name   ON Voters (full_name);
CREATE INDEX idx_voters_gender      ON Voters (gender);


-- ------------------------------------------------------------
-- TABLE: AuditLogs
-- Tracks all data-modification actions by administrators.
-- ------------------------------------------------------------
CREATE TABLE AuditLogs (
    log_id       INT           NOT NULL AUTO_INCREMENT,
    user_id      INT           NOT NULL,
    action       VARCHAR(20)   NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    target_table VARCHAR(50)   NOT NULL,
    target_id    INT           NOT NULL,
    timestamp    DATETIME      NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_audit_logs    PRIMARY KEY (log_id),
    CONSTRAINT fk_audit_user    FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Indexes on foreign key and timestamp for audit trail queries
CREATE INDEX idx_audit_user_id    ON AuditLogs (user_id);
CREATE INDEX idx_audit_timestamp  ON AuditLogs (timestamp);
CREATE INDEX idx_audit_target     ON AuditLogs (target_table, target_id);

-- ============================================================
-- END OF DDL
-- ============================================================
