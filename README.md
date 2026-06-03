# digiVIMS — Digital Voter Information & Management System

> A comprehensive Django-based web application for managing voter information, families, polling stations, and audit logs in a secure, role-based environment.

## 🎯 Features

- **User Authentication**: Secure login with session-based authentication
- **Dashboard**: Real-time statistics and recent activity overview
- **Voter Management**: Full CRUD operations with CNIC-based uniqueness
- **Family Management**: Group voters into household units (Gharanas)
- **Polling Stations**: Track voting locations and capacity management
- **Audit Logs**: Comprehensive logging of all admin actions
- **Role-Based Access**: Admin vs Viewer role separation
- **Advanced Search**: Filter voters by CNIC, name, family, or station
- **Responsive UI**: Mobile-friendly interface with dark theme (Bootstrap 5)

## 📋 Project Structure

```
digiVIMS/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── setup.bat / setup.sh         # Automated setup scripts
├── .env.example                 # Environment template
├── DEPLOYMENT.md                # Deployment instructions
├── IMPLEMENTATION_GUIDE.txt     # Implementation notes
│
├── vims_project/                # Project configuration
│   ├── settings.py              # Settings (env-ready)
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI app
│   └── __init__.py
│
├── voter_app/                   # Main application
│   ├── models.py                # 5 ORM models (managed=False)
│   ├── views.py                 # All CRUD + search + dashboard
│   ├── forms.py                 # Django ModelForms
│   ├── urls.py                  # App URL patterns
│   └── __init__.py
│
└── templates/voter_app/         # HTML templates
    ├── base.html                # Layout wrapper
    ├── login.html               # Authentication
    ├── dashboard.html           # Overview
    ├── voter_list.html          # Voter list & search
    ├── voter_detail.html        # Voter detail view
    ├── voter_form.html          # Add/Edit voter
    ├── family_list.html         # Family list
    ├── family_detail.html       # Family detail & members
    ├── family_form.html         # Add/Edit family
    ├── station_list.html        # Station list
    ├── station_detail.html      # Station detail & capacity
    ├── station_form.html        # Add/Edit station
    ├── confirm_delete.html      # Delete confirmation
    ├── audit_logs.html          # Activity audit trail
    └── _detail_field.html       # Reusable field component
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Configure database:**
Copy `.env.example` to `.env` and update:
```
DB_PASSWORD=your_mysql_password
```

**3. Run migrations:**
```bash
python manage.py migrate
```

**4. Create admin user:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.hashers import make_password
from voter_app.models import Users

Users.objects.create(
    username='admin',
    password_hash=make_password('your_password'),
    role='admin'
)
exit()
```

**5. Start development server:**
```bash
python manage.py runserver
```

**6. Open in browser:**
```
http://127.0.0.1:8000/
```

## 🔑 Login Credentials

After setup, use:
- **Username:** `admin`
- **Password:** The one you set during admin user creation

## 📊 Database Schema

The application integrates with an existing MySQL schema containing 5 tables:

| Table | Purpose | ORM Model | Managed |
|-------|---------|-----------|---------|
| `users` | System accounts | `Users` | ❌ |
| `voters` | Voter records | `Voters` | ❌ |
| `families` | Household groups | `Families` | ❌ |
| `pollingstations` | Voting locations | `PollingStations` | ❌ |
| `auditlogs` | Admin actions | `AuditLogs` | ❌ |

**Note:** All models have `managed=False` — Django does not create/alter/drop these tables.

## 🔒 Security Features

- ✅ CSRF protection on all forms
- ✅ Password hashing (PBKDF2)
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ Audit logging of all changes
- ✅ SQL injection prevention (ORM)
- ✅ Secure cookies (HTTPOnly, SameSite)

## 🛠 Configuration

### Environment Variables

Create a `.env` file with:
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=vims_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### Settings Reference

All settings are in `vims_project/settings.py`:
- Database config via environment variables
- Templates configured for `templates/` folder
- Session backend: Database
- Session timeout: 1 hour
- Static files configuration

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `Table 'vims_db.voters' doesn't exist` | Verify MySQL database `vims_db` exists with schema |
| `Access denied for user 'root'` | Check `DB_PASSWORD` in `.env` |
| `No module named 'MySQLdb'` | Windows: `pip install PyMySQL` then add to `vims_project/__init__.py`: `import pymysql; pymysql.install_as_MySQLdb()` |
| `TemplateDoesNotExist: voter_app/base.html` | Verify `TEMPLATES['DIRS']` includes `BASE_DIR / 'templates'` in settings.py |
| `CSRF verification failed` | Ensure `{% csrf_token %}` is in all forms |

## 📚 API Endpoints

All endpoints require login. Admin operations are restricted.

### Authentication
- `GET /` → Login page
- `GET /logout/` → Logout

### Dashboard
- `GET /dashboard/` → Overview (logged-in users only)

### Voters
- `GET /voters/` → List with search/filter
- `GET /voters/add/` → Create form (admin)
- `POST /voters/add/` → Save voter (admin)
- `GET /voters/<id>/` → Voter detail
- `GET /voters/<id>/edit/` → Edit form (admin)
- `POST /voters/<id>/edit/` → Update voter (admin)
- `GET /voters/<id>/delete/` → Delete confirmation (admin)
- `POST /voters/<id>/delete/` → Delete voter (admin)

### Families
- `GET /families/` → List with pagination
- `GET /families/add/` → Create form (admin)
- `GET /families/<id>/` → Family detail & members
- `GET /families/<id>/edit/` → Edit form (admin)
- `GET /families/<id>/delete/` → Delete confirmation (admin)

### Polling Stations
- `GET /stations/` → List all stations
- `GET /stations/add/` → Create form (admin)
- `GET /stations/<id>/` → Station detail with capacity
- `GET /stations/<id>/edit/` → Edit form (admin)
- `GET /stations/<id>/delete/` → Delete confirmation (admin)

### Admin
- `GET /audit/` → Audit logs (admin only)

## 🎨 Design System

The application uses a sophisticated dark theme with:
- **Primary:** Teal accent (#0EA87A)
- **Background:** Navy dark (#0B1426)
- **Typography:** IBM Plex Sans + Barlow Condensed
- **Icons:** Bootstrap Icons
- **Framework:** Bootstrap 5

## 📈 Development

### Running Tests
```bash
python manage.py test voter_app
```

### Creating Superuser
```bash
python manage.py createsuperuser
```
(Note: This is separate from digiVIMS users table)

### Collecting Static Files
```bash
python manage.py collectstatic
```

## 🚀 Production Deployment

For production, update `vims_project/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')  # Use strong key from env
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
```

Use a production WSGI server:
```bash
pip install gunicorn
gunicorn vims_project.wsgi:application --bind 0.0.0.0:8000
```

Or with uWSGI:
```bash
pip install uwsgi
uwsgi --http :8000 --wsgi-file vims_project/wsgi.py --master --processes 4 --threads 2
```

## 📞 Support

For issues or questions:
1. Check `DEPLOYMENT.md` for setup troubleshooting
2. Review `IMPLEMENTATION_GUIDE.txt` for schema details
3. Verify database connection in `.env`
4. Check Django logs: `python manage.py runserver` output

## 📄 License

Internal project for voter information management.

---

**Version:** 1.0  
**Last Updated:** June 2026  
**Status:** Ready for Deployment ✅
