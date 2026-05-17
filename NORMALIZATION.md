# VIMS — Normalization Document (Milestone 2)

**Project:** Digital Voter Information & Management System  
**Group:** Suhaib Ahmad & Muhammad Rehan Khan  
**Course:** Database Systems Lab  

---

## Overview

This document applies First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF) to every table in the VIMS schema. Where a normal form is already satisfied without changes, a justification is provided explaining why no change was needed.

---

## Table 1: `Users`

**Columns:** `user_id`, `username`, `password_hash`, `role`

### 1NF
**Requirement:** All columns must be atomic (indivisible), each column must hold a single value, and the table must have a primary key.

**Analysis:**
- `user_id` is an integer primary key — unique and not null. ✓
- `username` holds a single string value per row. ✓
- `password_hash` holds a single bcrypt/hash string. ✓
- `role` is an ENUM with exactly one value per row ('Administrator' or 'Viewer'). ✓
- No repeating groups or multi-valued attributes exist.

**Result:** No change needed. The `Users` table already satisfies 1NF.

### 2NF
**Requirement:** Must be in 1NF AND every non-key attribute must be fully functionally dependent on the entire primary key (no partial dependencies).

**Analysis:**
- The primary key is a single column: `user_id`.
- With a single-column primary key, partial dependency is impossible by definition — a partial dependency requires a composite key where a non-key attribute depends on only *part* of the key.
- All of `username`, `password_hash`, and `role` depend entirely on `user_id`.

**Result:** No change needed. 2NF is satisfied.

### 3NF
**Requirement:** Must be in 2NF AND no non-key attribute should transitively depend on the primary key through another non-key attribute.

**Analysis:**
- Does `role` determine `password_hash`? No — two users can share the same role but have different passwords.
- Does `username` determine `role`? No — the role of a user is independent of their username.
- There are no hidden functional dependencies among `username`, `password_hash`, and `role`.

**Result:** No change needed. 3NF is satisfied.

---

## Table 2: `PollingStations`

**Columns:** `station_id`, `name`, `location_code`, `city`, `capacity`

### 1NF
**Analysis:**
- `station_id` is an integer primary key. ✓
- `name`, `location_code`, `city` are each single-valued string attributes. ✓
- `capacity` is a single integer. ✓
- No column stores a list or set of values.

**Result:** No change needed. 1NF is satisfied.

### 2NF
**Analysis:**
- Primary key is the single column `station_id`, so partial dependencies cannot occur.
- `name`, `location_code`, `city`, and `capacity` all describe a specific polling station identified by `station_id`.

**Result:** No change needed. 2NF is satisfied.

### 3NF
**Analysis:**
- Potential concern: Could `location_code` → `city` be a transitive dependency (i.e., `station_id` → `location_code` → `city`)?
- In this schema, `location_code` is a formatted identifier assigned *to the station itself* (e.g., `PSH-001`), not a lookup code that independently determines a city from an external reference table. The city is a direct attribute of the station, not derived from the location code.
- `location_code` is marked UNIQUE and serves as an alternate key for the station, not a foreign key into a Cities table. Therefore, `city` depends directly on `station_id` (the primary key), not transitively through `location_code`.
- `capacity` depends only on `station_id` and is not derivable from any other non-key column.

**Result:** No change needed. 3NF is satisfied.

---

## Table 3: `Families`

**Columns:** `family_id`, `head_name`, `permanent_address`

### 1NF
**Analysis:**
- `family_id` is an integer primary key. ✓
- `head_name` is a single string value per family. ✓
- `permanent_address` is stored as TEXT — a single address string per family, not a list. ✓

**Result:** No change needed. 1NF is satisfied.

### 2NF
**Analysis:**
- Single-column primary key `family_id` — partial dependency is impossible.
- `head_name` and `permanent_address` are properties of the family record identified by `family_id`.

**Result:** No change needed. 2NF is satisfied.

### 3NF
**Analysis:**
- Does `head_name` determine `permanent_address`? No — two families could have a head with the same name but live at different addresses.
- Does `permanent_address` determine `head_name`? No — multiple families could share an address (e.g., adjacent units) without sharing a head.
- No transitive dependency exists between the two non-key attributes.

**Result:** No change needed. 3NF is satisfied.

---

## Table 4: `Voters`

**Columns:** `voter_id`, `cnic`, `full_name`, `age`, `gender`, `family_id` (FK), `station_id` (FK)

### 1NF
**Analysis:**
- `voter_id` is an integer primary key. ✓
- `cnic` is a CHAR(15) — single atomic value per voter. ✓
- `full_name` is a single VARCHAR value. ✓
- `age` is a single integer. ✓
- `gender` is an ENUM — exactly one value per row. ✓
- `family_id` and `station_id` are single integer foreign keys — no repeating groups.

**Result:** No change needed. 1NF is satisfied.

### 2NF
**Analysis:**
- Single-column primary key `voter_id` — partial dependency is impossible.
- All attributes (`cnic`, `full_name`, `age`, `gender`, `family_id`, `station_id`) describe the individual voter identified by `voter_id`.

**Result:** No change needed. 2NF is satisfied.

### 3NF
**Analysis:**
- Could `cnic` → `full_name`? CNIC is a unique national ID that does identify one person, so technically `cnic` could determine `full_name`. However, `cnic` is itself an alternate key (UNIQUE constraint) of the `Voters` table, not merely a non-key attribute. Functional dependency from one candidate key to another does not constitute a 3NF violation. This is a standard accepted design pattern.
- `age` and `gender` depend on the specific voter (identified by `voter_id`), not on any other non-key attribute.
- `family_id` and `station_id` are foreign key references, not transitive dependencies — they establish relational links to other entities.

**Result:** No change needed. 3NF is satisfied.

---

## Table 5: `AuditLogs`

**Columns:** `log_id`, `user_id` (FK), `action`, `target_table`, `target_id`, `timestamp`

### 1NF
**Analysis:**
- `log_id` is an integer primary key. ✓
- `user_id` is a single integer foreign key. ✓
- `action` is a VARCHAR storing one operation type ('INSERT', 'UPDATE', or 'DELETE') per row. ✓
- `target_table` is a single VARCHAR storing the name of the affected table. ✓
- `target_id` is a single integer. ✓
- `timestamp` is a single DATETIME value. ✓

**Result:** No change needed. 1NF is satisfied.

### 2NF
**Analysis:**
- Single-column primary key `log_id` — partial dependency is impossible.
- All attributes fully describe a single audit event identified by `log_id`.

**Result:** No change needed. 2NF is satisfied.

### 3NF
**Analysis:**
- Does `action` determine `target_table`? No — the same action type (e.g., 'UPDATE') can be performed on any table.
- Does `target_table` determine `target_id`? No — `target_id` is the primary key of the record in the affected table, which only makes sense in the context of a specific log entry (`log_id`), not the table name alone.
- `timestamp` is determined solely by when the log entry was created — it does not depend on any other non-key attribute.

**Result:** No change needed. 3NF is satisfied.

---

## Duplicate / Redundancy Check

| Potential Redundancy | Decision |
|---|---|
| `city` could be repeated across many `PollingStations` rows if multiple stations exist in the same city | Acceptable — `city` is a direct attribute of each station record, not a shared lookup. No Cities reference table is needed at this project scope. |
| `action` values in `AuditLogs` repeat ('INSERT', 'UPDATE', 'DELETE') | Acceptable — ENUM or restricted VARCHAR is standard. Extracting to a lookup table would add unnecessary complexity for 3 fixed values. |
| `head_name` in `Families` could theoretically match a `full_name` in `Voters` | These are different entities (family head vs registered voter). No duplication issue. |

No structural changes were required from the redundancy check.

---

## Final Schema (Post-Normalization — Unchanged)

The schema produced in Milestone 1 is in **Third Normal Form (3NF)** across all five tables. No tables were split, no columns were moved, and no new tables were introduced. The justifications above confirm this conclusion with explicit reasoning for each table and each normal form level.

```
Users        (user_id PK, username UNIQUE, password_hash, role)
PollingStations (station_id PK, name, location_code UNIQUE, city, capacity)
Families     (family_id PK, head_name, permanent_address)
Voters       (voter_id PK, cnic UNIQUE, full_name, age, gender, family_id FK, station_id FK)
AuditLogs    (log_id PK, user_id FK, action, target_table, target_id, timestamp)
```
