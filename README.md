# Digital Voter Information & Management System (VIMS)

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

## Project Overview
The **Digital Voter Information & Management System (VIMS)** is a web-based solution designed to modernize electoral management. By transitioning from manual paper-based registers to a centralized relational database, VIMS ensures high-speed data retrieval, eliminates redundancy (ghost voters), and provides structured mapping of family units (**"Gharanas"**) and polling station assignments.

This project is developed as part of the **Database (Lab)** requirements at **IMSciences**.

---

## Project Team
*   **Suhaib Ahmad** – BS Software Engineering (Group B)
*   **Muhammad Rehan Khan** – BS Software Engineering (Group B)

---

## Tech Stack
*   **Backend:** Python 3.x, Django Framework
*   **Database:** MySQL 8.0
*   **Frontend:** HTML5, CSS3, Bootstrap 5
*   **Development Tools:** VS Code, MySQL Workbench

---

## Database Design & Relationship Logic
The core of VIMS is its relational schema, designed to enforce entity and referential integrity.

### Primary Entities:
*   **Users:** System access control with role-based authorization (Admin vs. Viewer).
*   **Voters:** The central entity containing demographic data and unique identifiers (CNIC).
*   **Families:** Groups voters into "Gharanas" via `family_id` foreign keys.
*   **Polling Stations:** Manages geographic distribution and voter capacity.

### Key Database Features:
*   **Integrity:** `UNIQUE` constraints on CNICs to prevent duplicate registrations.
*   **Relational Mapping:** `ON DELETE CASCADE` and `SET NULL` rules to manage orphaned records.
*   **Performance:** Indexed search queries for sub-second verification.

---

## Key Features
*   **Advanced Search:** Instant lookup by CNIC, Name, or Family ID.
*   **Family Unit Roster:** View all registered voters within a specific household.
*   **Station Management:** Filter voters by polling station and monitor station capacity.
*   **Admin Dashboard:** Full CRUD (Create, Read, Update, Delete) operations for authorized personnel.
*   **Analytics:** Visual distribution of gender and voter density per station.

---

## Project Structure (Planned)
```text
├── vims_project/          # Django project settings
├── voter_app/             # Main application logic
│   ├── models.py          # MySQL Database Schema
│   ├── views.py           # Logic for Search and Filtering
│   ├── templates/         # HTML Interfaces
│   └── static/            # CSS and Bootstrap assets
├── manage.py              # Django CLI
└── requirements.txt       # Project dependencies
