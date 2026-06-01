"""
VIMS — Synthetic Data Generator (Milestone 3)
Generates realistic CSV files for all five VIMS tables using Faker.
Authors: Suhaib Ahmad, Muhammad Rehan Khan

Install dependency:  pip install faker
Run:                 python generate_data.py
Output:              data/ directory with 5 CSV files
"""

import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_PK')   # Pakistan locale for realistic names
random.seed(42)
fake.seed_instance(42)

os.makedirs('data', exist_ok=True)

# ---------------------------------------------------------------
# CONFIG — row counts (all >= 50 as required)
# ---------------------------------------------------------------
NUM_USERS            = 15    # Small — system staff only
NUM_POLLING_STATIONS = 20
NUM_FAMILIES         = 80
NUM_VOTERS           = 150
NUM_AUDIT_LOGS       = 100

# ---------------------------------------------------------------
# 1. USERS
# ---------------------------------------------------------------
print("Generating users.csv ...")

ADMIN_NAMES = [
    'admin_suhaib', 'admin_rehan', 'admin_tariq', 'admin_bilal',
    'admin_nasir', 'admin_zubair'
]
VIEWER_NAMES = [
    'viewer_01', 'viewer_02', 'viewer_03', 'viewer_04',
    'viewer_05', 'viewer_06', 'viewer_07', 'viewer_08', 'viewer_09'
]

users = []
user_id = 1
for name in ADMIN_NAMES:
    users.append({
        'user_id':       user_id,
        'username':      name,
        'password_hash': fake.sha256(),
        'role':          'Administrator'
    })
    user_id += 1
for name in VIEWER_NAMES:
    users.append({
        'user_id':       user_id,
        'username':      name,
        'password_hash': fake.sha256(),
        'role':          'Viewer'
    })
    user_id += 1

with open('data/users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id','username','password_hash','role'])
    writer.writeheader()
    writer.writerows(users)
print(f"  -> {len(users)} rows written.")

# ---------------------------------------------------------------
# 2. POLLING STATIONS (KPK cities)
# ---------------------------------------------------------------
print("Generating polling_stations.csv ...")

KPK_CITIES = [
    'Peshawar', 'Mardan', 'Abbottabad', 'Swat', 'Nowshera',
    'Charsadda', 'Kohat', 'Dera Ismail Khan', 'Mansehra', 'Haripur'
]

stations = []
location_codes_used = set()
for i in range(1, NUM_POLLING_STATIONS + 1):
    city = random.choice(KPK_CITIES)
    city_code = ''.join(w[0] for w in city.split()).upper()[:3]
    loc_code = f"{city_code}-{i:03d}"
    # Ensure uniqueness
    while loc_code in location_codes_used:
        loc_code = f"{city_code}-{random.randint(100,999)}"
    location_codes_used.add(loc_code)

    stations.append({
        'station_id':    i,
        'name':          f"Polling Station {loc_code}",
        'location_code': loc_code,
        'city':          city,
        'capacity':      random.choice([300, 400, 500, 600, 750, 1000])
    })

with open('data/polling_stations.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['station_id','name','location_code','city','capacity'])
    writer.writeheader()
    writer.writerows(stations)
print(f"  -> {len(stations)} rows written.")

# ---------------------------------------------------------------
# 3. FAMILIES
# ---------------------------------------------------------------
print("Generating families.csv ...")

ADDRESSES = [
    'House {n}, Gul Bahar Colony, Peshawar',
    'Street {n}, Hayatabad Phase 2, Peshawar',
    'Plot {n}, Warsak Road, Peshawar',
    'House {n}, University Town, Peshawar',
    'Flat {n}, Gulberg Road, Mardan',
    'House {n}, Cantt Area, Abbottabad',
    'Village {n}, Mingora, Swat',
    'Mohalla {n}, Nowshera Kalan',
    'House {n}, Rustam Road, Mardan',
    'Plot {n}, Kohat Road, Peshawar',
]

families = []
for i in range(1, NUM_FAMILIES + 1):
    addr_template = random.choice(ADDRESSES)
    address = addr_template.replace('{n}', str(random.randint(1, 999)))
    families.append({
        'family_id':         i,
        'head_name':         fake.name_male(),
        'permanent_address': address
    })

with open('data/families.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['family_id','head_name','permanent_address'])
    writer.writeheader()
    writer.writerows(families)
print(f"  -> {len(families)} rows written.")

# ---------------------------------------------------------------
# 4. VOTERS
# ---------------------------------------------------------------
print("Generating voters.csv ...")

def random_cnic():
    """Generate a realistic 15-digit Pakistani CNIC (without dashes)."""
    # Format: XXXXXYYYYYYY Z  (5 province+district, 7 serial, 1 gender digit)
    province = random.choice(['1', '2', '3', '4', '5', '6', '7'])
    district = str(random.randint(1, 9)).zfill(4)
    serial   = str(random.randint(1000000, 9999999))
    check    = str(random.randint(1, 9))
    return province + district + serial + check  # 13 digits

cnic_set = set()
voters = []
family_ids = [f['family_id'] for f in families]
station_ids = [s['station_id'] for s in stations]

for i in range(1, NUM_VOTERS + 1):
    # Unique CNIC
    cnic = random_cnic()
    attempts = 0
    while cnic in cnic_set and attempts < 1000:
        cnic = random_cnic()
        attempts += 1
    cnic_set.add(cnic)

    gender = random.choices(['Male', 'Female', 'Other'], weights=[55, 44, 1])[0]
    name   = fake.name_male() if gender == 'Male' else fake.name_female()

    voters.append({
        'voter_id':  i,
        'cnic':      cnic,
        'full_name': name,
        'age':       random.randint(18, 75),
        'gender':    gender,
        'family_id': random.choice(family_ids),
        'station_id':random.choice(station_ids)
    })

with open('data/voters.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['voter_id','cnic','full_name','age','gender','family_id','station_id'])
    writer.writeheader()
    writer.writerows(voters)
print(f"  -> {len(voters)} rows written.")

# ---------------------------------------------------------------
# 5. AUDIT LOGS
# ---------------------------------------------------------------
print("Generating audit_logs.csv ...")

admin_user_ids = [u['user_id'] for u in users if u['role'] == 'Administrator']
target_tables  = ['Voters', 'Families', 'PollingStations']
actions        = ['INSERT', 'UPDATE', 'DELETE']
action_weights = [50, 35, 15]   # INSERTs most common

base_time = datetime(2025, 1, 1, 8, 0, 0)
audit_logs = []
for i in range(1, NUM_AUDIT_LOGS + 1):
    base_time += timedelta(minutes=random.randint(5, 120))
    table = random.choice(target_tables)
    # target_id picks from the right pool
    if table == 'Voters':
        tid = random.randint(1, NUM_VOTERS)
    elif table == 'Families':
        tid = random.randint(1, NUM_FAMILIES)
    else:
        tid = random.randint(1, NUM_POLLING_STATIONS)

    audit_logs.append({
        'log_id':       i,
        'user_id':      random.choice(admin_user_ids),
        'action':       random.choices(actions, weights=action_weights)[0],
        'target_table': table,
        'target_id':    tid,
        'timestamp':    base_time.strftime('%Y-%m-%d %H:%M:%S')
    })

with open('data/audit_logs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['log_id','user_id','action','target_table','target_id','timestamp'])
    writer.writeheader()
    writer.writerows(audit_logs)
print(f"  -> {len(audit_logs)} rows written.")

# ---------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------
print("\n✔ All CSV files generated in ./data/")
print(f"  users.csv            — {len(users)} rows")
print(f"  polling_stations.csv — {len(stations)} rows")
print(f"  families.csv         — {len(families)} rows")
print(f"  voters.csv           — {len(voters)} rows")
print(f"  audit_logs.csv       — {len(audit_logs)} rows")
