# TruthLens

TruthLens is a Django-based forensic media analysis platform for video, audio, and image deepfake detection.

## Run In VS Code

Open this folder in VS Code:

`C:\Users\LENOVO\Documents\Codex\2026-04-22-here-s-a-comprehensive-professional-prompt`

Then run in the integrated PowerShell terminal:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`

## SQL Database Setup

TruthLens now supports:

- SQLite for local development
- PostgreSQL for a production-style SQL setup
- MySQL through Django's MySQL backend if you install the matching driver

Configuration is controlled through environment variables.

1. Create a local env file or set variables in PowerShell.
2. Pick the database engine.
3. Run migrations.

### SQLite

```powershell
$env:DB_ENGINE="sqlite"
python manage.py migrate
python manage.py runserver
```

### PostgreSQL

Make sure PostgreSQL is installed and that a database named `truthlens` exists.

```powershell
$env:DB_ENGINE="postgresql"
$env:DB_NAME="truthlens"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
python manage.py migrate
python manage.py runserver
```

### MySQL

If you want MySQL, install a Django-compatible MySQL driver first, then set:

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="truthlens"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
python manage.py migrate
python manage.py runserver
```

## Notes

- Local history is stored in the configured SQL database through the `DetectionRecord` and `AnalyticsSummary` models.
- If you stay on SQLite, the data lives in `db.sqlite3`.
- If you switch to PostgreSQL or MySQL, run `python manage.py migrate` again against that database.
