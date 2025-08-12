# Little Lemon Booking System

A Django-based web application for managing restaurant table bookings and menu pages.

## Features
- Booking creation and listing (restaurant app)
- Django Admin for data management
- Templated frontend (restaurant/templates)
- Static assets (restaurant/static)

## Tech Stack
- Python 3.11+ (works with 3.13)
- Django 4.1.x
- MySQL 8 (production) or SQLite (development)
- python-dotenv for environment variables
- Waitress (Windows) or Gunicorn (Linux) for production WSGI

## Project Structure (key parts)
- littlelemon/ — Django project (settings, urls, wsgi)
- restaurant/ — App (models, views, urls, templates, static)
- manage.py — Django management script

## Prerequisites
- Python installed and on PATH
- MySQL database (if using MySQL locally or in production)
- On Windows for MySQL: MySQL client libraries. If mysqlclient build fails, use SQLite for local dev.

## Setup (Windows)

1) Clone and open in VS Code  
2) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3) Install dependencies
```powershell
pip install "Django==4.1.1" python-dotenv mysqlclient waitress
```
Notes:
- If mysqlclient fails to install on Windows, you can either:
  - Install a prebuilt wheel for your Python version, or
  - Use SQLite for local development (see “Use SQLite locally” below).

4) Create a .env file in the project root
```
SECRET_KEY=replace-with-a-strong-secret
DB_NAME=your_mysql_db_name
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=your-mysql-hostname
DB_PORT=3306
# DB_SSL_CA=C:/path/to/ca.pem   # Optional, if your host requires SSL
```

The project reads these values in littlelemon/settings.py via python-dotenv.

5) Run migrations and create superuser
```powershell
python manage.py migrate
python manage.py createsuperuser
```

6) Start the development server
```powershell
python manage.py runserver
```
Visit http://127.0.0.1:8000 and http://127.0.0.1:8000/admin.

## Use SQLite locally (recommended if remote MySQL blocks connections)
If your hosting provider does not allow remote DB access from your PC, switch to SQLite for local development:

- In littlelemon/settings.py, temporarily set:
```python
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
  }
}
```
Then run:
```powershell
python manage.py migrate
```
Keep MySQL settings for production.

## Static Files
- Static URL is configured as `restaurant/static/` and sources from `restaurant/static/`.
- For production, collect and serve via a web server (see below).

Collect static files (production):
```powershell
python manage.py collectstatic
```

## Running in Production (Windows with Waitress)

1) Update settings for production
- In littlelemon/settings.py:
  - DEBUG = False
  - ALLOWED_HOSTS = ["your-domain.com", "your-server-ip"]
  - Optionally set:
    - CSRF_TRUSTED_ORIGINS = ["https://your-domain.com"]
    - SECURE_SSL_REDIRECT = True (behind HTTPS)
    - SESSION_COOKIE_SECURE = True
    - CSRF_COOKIE_SECURE = True

2) Ensure environment variables are set on the server (use the same .env keys).

3) Migrate and collect static files on the server
```powershell
python manage.py migrate
python manage.py collectstatic
```

4) Start with Waitress
```powershell
waitress-serve --port=8000 littlelemon.wsgi:application
```

Optional: run Waitress as a Windows Service (e.g., using NSSM) and reverse-proxy via IIS or Nginx for HTTPS/static.

## Running in Production (Linux with Gunicorn + Nginx) — high level
- pip install gunicorn
- gunicorn littlelemon.wsgi:application --bind 0.0.0.0:8000
- Configure Nginx to reverse proxy to Gunicorn and serve /static/ and /media/.
- Set DEBUG=False and proper ALLOWED_HOSTS as above.

## Database Notes and Troubleshooting
- OperationalError (2002) “timeout”: remote MySQL often blocks connections from local machines. Use SQLite locally or deploy the app to the same provider/network as the DB.
- “No database selected (1046)”: Ensure DB_NAME matches an existing database and your user has access.
- SSL: If your MySQL host requires SSL, add in settings:
```python
'OPTIONS': {
  'ssl': {
    'ca': os.getenv('DB_SSL_CA'),
    'verify_cert': True,
  }
}
```

## Common Commands
```powershell
# Install deps
pip install -r requirements.txt  # if you create one

# Make migrations for app changes
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run tests (if added)
python manage.py test
```

## Security Checklist (Production)
- DEBUG = False
- Strong SECRET_KEY via environment variable
- ALLOWED_HOSTS set correctly
- HTTPS enabled (TLS certificate)
- Secure cookies and SECURE_SSL_REDIRECT=True
- Regular dependency updates and backups