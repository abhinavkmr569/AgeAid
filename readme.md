# AgeAid — Health Trend Tracker

A privacy-first AI health dashboard that extracts data from blood reports, normalizes medical terms, and visualizes long-term trends. Self-hosted on a Raspberry Pi with Google Gemini.

## 🚀 Features

- **AI Extraction** — uses Google Gemini to read PDFs and images of lab reports.
- **Trend Analysis** — visualizes cholesterol, sugar, and thyroid levels over time.
- **Smart Auth** — sign in with Google (OAuth2) or email/password.
- **Privacy First** — "right to erasure" (delete account) built in.
- **Cost Tracking** — monitors AI token usage per report.
- **Dockerized** — app and database run together via Docker Compose, with Alembic migrations applied on startup.

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit (port 8501) |
| Backend | FastAPI (port 8502) |
| Database | PostgreSQL 15, running as a container |
| AI Engine | Google Gemini |
| Infrastructure | Docker Compose, Cloudflare Tunnel (for public access) |

> **Note:** this project previously ran on CockroachDB Serverless. It now uses a local
> Postgres container, so the old `root.crt` / `sslmode=verify-full` certificate setup is
> no longer needed.

## 📂 Project Structure

```
health_backend/
├── alembic/             # Database migration scripts (alembic/versions/)
├── alembic.ini          # Alembic config; connection string comes from DATABASE_URL
├── app.py               # Streamlit frontend
├── main.py              # FastAPI backend
├── database.py          # SQLAlchemy engine and session
├── models.py            # SQLAlchemy tables
├── schemas.py           # Pydantic models
├── extractor.py         # Gemini AI logic
├── normalizer.py        # Medical term normalization
├── clusters.py          # Related-test grouping
├── utils.py             # Date helpers
├── Dockerfile           # App image; runs migrations, then FastAPI + Streamlit
├── docker-compose.yml   # App + Postgres
├── deploy.sh            # Pull, rebuild, restart (Raspberry Pi)
└── .env                 # Secrets (gitignored)
```

Maintenance scripts: `check_users.py`, `clear_reports.py`, `reset_db.py`, and
`nuclear_reset.py` (destructive — drops data).

## ⚡ Quick Start

**Prerequisites:** Docker Desktop. (Python 3.11+ only if you want to run outside Docker.)

### 1. Create your `.env`

Every variable below is required. `POSTGRES_PASSWORD` **must** match the password
inside `DATABASE_URL`, since Compose uses it to initialize the database container.

```ini
# AI
GEMINI_API_KEY=your_key

# Database. The host is "db" — the Compose service name, not localhost.
POSTGRES_PASSWORD=choose_a_password
DATABASE_URL=postgresql://healthuser:choose_a_password@db:5432/healthdb

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Session signing. There is no default — the app refuses to start without it.
SECRET_KEY=some_long_random_string

# URLs
ENV_TYPE=development
PUBLIC_API_URL=http://localhost:8502   # FastAPI, for browser-facing OAuth redirects
FRONTEND_URL=http://localhost:8501     # where users land after a Google login
```

In production both point at your public domain, e.g. `https://your-domain.com`.

Compose parses `.env` strictly: every non-comment line must be `KEY=value`. Stray prose
or separator lines will make `docker compose up` fail to read the file.

### 2. Run

```bash
docker compose up -d --build
```

This starts Postgres, waits for it to accept connections, applies the Alembic
migrations, then launches FastAPI and Streamlit.

Open the UI at **http://localhost:8501**.

```bash
docker compose logs -f app     # tail logs
docker compose down            # stop (keeps data)
docker compose down -v         # stop and DELETE the database volume
```

## 🍓 Raspberry Pi Deployment

```bash
git clone <repo_url>
cd health_backend
nano .env          # set ENV_TYPE=production and PUBLIC_API_URL=https://your-domain.com
./deploy.sh
```

`deploy.sh` pulls the latest code and runs `docker compose up -d --build`.

## 🔄 Database Migrations (Alembic)

Migrations run automatically on container startup. Alembic reads the connection string
from `DATABASE_URL`; it is **not** configured in `alembic.ini`.

To create a migration after changing `models.py`:

```bash
# 1. Enter the app container
docker compose exec app /bin/bash

# 2. Generate the script
alembic revision --autogenerate -m "Description of change"

# 3. Apply it
alembic upgrade heads
```

Commit the generated file in `alembic/versions/`. Keep the history to a **single head** —
if `alembic heads` prints more than one revision, `upgrade` will fail.

## 🛡️ Traffic Flow (Cloudflare Tunnel)

Route auth traffic to FastAPI and everything else to Streamlit:

| Public hostname | Origin |
| --- | --- |
| `your-domain.com/auth*` | `http://localhost:8502` (FastAPI) |
| `your-domain.com/` | `http://localhost:8501` (Streamlit) |

## 🔐 Secrets

`.env`, `keys.txt`, and the Google `client_secret_*.json` are gitignored and excluded
from the Docker image via `.dockerignore`. Never commit them — and note that adding a
secret to `.gitignore` does not remove it from history if it was committed previously.
