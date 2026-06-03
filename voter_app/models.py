# voter_app/models.py
# digiVIMS — Digital Voter Information & Management System
# Django ORM models mapped to the existing MySQL schema.
# managed = False on all models → Django will NOT create/alter/drop
# these tables (they already exist in your MySQL database).

from django.db import models


# ─────────────────────────────────────────────
# 1. USERS
#    Stores system accounts with role-based access.
#    No FK dependencies — must be populated first.
# ─────────────────────────────────────────────
class Users(models.Model):

    ROLE_CHOICES = [
        ('Administrator',  'Administrator'),
        ('Viewer', 'Viewer'),
    ]

    user_id       = models.AutoField(primary_key=True)
    username      = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    role          = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Viewer')

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        managed  = False          # DB table already exists
        db_table = 'users'


# ─────────────────────────────────────────────
# 2. POLLING STATIONS
#    Geographic assignment points for voters.
#    No FK dependencies — must be populated first.
# ─────────────────────────────────────────────
class PollingStations(models.Model):

    station_id    = models.AutoField(primary_key=True)
    name          = models.CharField(max_length=100)
    location_code = models.CharField(max_length=20)
    city          = models.CharField(max_length=50)
    capacity      = models.IntegerField()

    def __str__(self):
        return f"{self.name} — {self.city}"

    class Meta:
        managed  = False
        db_table = 'pollingstations'


# ─────────────────────────────────────────────
# 3. FAMILIES  (Gharanas)
#    Groups voters into household units.
#    No FK dependencies — must be populated first.
# ─────────────────────────────────────────────
class Families(models.Model):

    family_id         = models.AutoField(primary_key=True)
    head_name         = models.CharField(max_length=100)
    permanent_address = models.TextField()

    def __str__(self):
        return f"Family #{self.family_id} — {self.head_name}"

    class Meta:
        managed  = False
        db_table = 'families'


# ─────────────────────────────────────────────
# 4. VOTERS
#    Central entity. References both Families and
#    PollingStations via FK → populated after both.
#
#    FK behaviour (matches your DDL):
#      family_id  → SET NULL on delete
#      station_id → SET NULL on delete
# ─────────────────────────────────────────────
class Voters(models.Model):

    GENDER_CHOICES = [
        ('Male',   'Male'),
        ('Female', 'Female'),
    ]

    voter_id  = models.AutoField(primary_key=True)
    cnic      = models.CharField(max_length=15, unique=True)   # UNIQUE — no ghost voters
    full_name = models.CharField(max_length=100)
    age       = models.PositiveSmallIntegerField()             # TINYINT UNSIGNED in MySQL
    gender    = models.CharField(max_length=6, choices=GENDER_CHOICES)

    # FK → families.family_id
    family = models.ForeignKey(
        Families,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='family_id',          # exact column name in MySQL
        related_name='voters',
    )

    # FK → pollingstations.station_id
    station = models.ForeignKey(
        PollingStations,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='station_id',         # exact column name in MySQL
        related_name='voters',
    )

    def __str__(self):
        return f"{self.full_name} | CNIC: {self.cnic}"

    class Meta:
        managed  = False
        db_table = 'voters'


# ─────────────────────────────────────────────
# 5. AUDIT LOGS
#    Tracks every admin action (INSERT/UPDATE/DELETE).
#    References Users — populated last.
#
#    FK behaviour:
#      user_id → SET NULL on delete (log preserved
#                even if the user account is removed)
# ─────────────────────────────────────────────
class AuditLogs(models.Model):

    log_id       = models.AutoField(primary_key=True)

    # FK → users.user_id
    user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',            # exact column name in MySQL
        related_name='audit_logs',
    )

    action       = models.CharField(max_length=20)   # e.g. 'INSERT', 'UPDATE', 'DELETE'
    target_table = models.CharField(max_length=50)   # e.g. 'voters', 'families'
    target_id    = models.IntegerField()             # PK of the affected row
    timestamp    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.action} on {self.target_table} (id={self.target_id})"

    class Meta:
        managed  = False
        db_table = 'auditlogs'
        ordering = ['-timestamp']        # newest logs first
