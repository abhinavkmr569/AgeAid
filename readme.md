# AgeAid - Health Trend Tracker (SaaS)

A privacy-first AI health dashboard that extracts data from blood reports, normalizes medical terms, and visualizes long-term trends. Self-hosted on Raspberry Pi with Google Gemini AI.ShutterstockExplore🚀 FeaturesAI Extraction: Uses Google Gemini 2.5 Flash to read PDF/Images.Trend Analysis: Visualizes cholesterol, sugar, and thyroid levels over time.Smart Auth: Sign in with Google (OAuth2) or Email/Password.Privacy First: "Right to Erasure" (Delete Account) built-in.Cost Tracking: Monitors AI token usage and costs per report.Production Ready: Dockerized with automated migrations (Alembic).🛠️ Tech StackFrontend: Streamlit (Python)Backend: FastAPI (Python)Database: CockroachDB Serverless (PostgreSQL compatible)AI Engine: Google Gemini 2.5 Flash & ProInfrastructure: Docker, Cloudflare Tunnel (for public access)📂 Project Structurehealth_backend/
├── alembic/             # Database migration scripts
├── app.py               # Streamlit Frontend
├── main.py              # FastAPI Backend
├── database.py          # DB Connection (SSL aware)
├── extractor.py         # Gemini AI Logic
├── models.py            # SQLAlchemy Tables
├── schemas.py           # Pydantic Models
├── deploy.sh            # One-click deployment script
├── get_cert.py          # SSL Certificate downloader
├── root.crt             # CockroachDB CA Certificate (Required)
└── .env                 # Secrets (GitIgnored)
⚡ Quick Start (Local Development)Prerequisites: Python 3.11+, Docker Desktop.Environment Variables (.env):GEMINI_API_KEY=your_key
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=verify-full

# Google Auth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
SECRET_KEY=random_string

# Local Dev Config
ENV_TYPE=development
PUBLIC_API_URL=http://localhost:8080
SSL Certificate (Windows):Run this in PowerShell to place the cert where local Python finds it:New-Item -ItemType Directory -Force -Path "$env:APPDATA\postgresql"
Invoke-WebRequest -Uri "[https://letsencrypt.org/certs/isrgrootx1.pem](https://letsencrypt.org/certs/isrgrootx1.pem)" -OutFile "$env:APPDATA\postgresql\root.crt"
Run with Docker:docker build -t health-app .
docker run -d -p 8080:8080 -p 8501:8501 --env-file .env health-app
Access UI at http://localhost:8501.🍓 Raspberry Pi Deployment (Production)Clone & Configure:git clone <repo_url>
cd health_backend
nano .env
# Set ENV_TYPE=production
# Set PUBLIC_API_URL=[https://your-domain.com](https://your-domain.com)
Download SSL Cert (Critical):Docker needs this file in the build context.python get_cert.py
# OR
curl -o root.crt [https://letsencrypt.org/certs/isrgrootx1.pem](https://letsencrypt.org/certs/isrgrootx1.pem)
Deploy:Use the automated script to pull, rebuild, and restart:chmod +x deploy.sh
./deploy.sh
🔄 Database Migrations (Alembic)The deploy.sh script runs migrations automatically on startup.To create a new migration after modifying models.py:# 1. Enter container
docker exec -it health-server /bin/bash

# 2. Generate script
alembic revision --autogenerate -m "Description of change"

# 3. Apply (Optional, usually handled by upgrade head)
alembic upgrade head
Note: Commit the generated file in alembic/versions to GitHub.🛡️ Traffic Flow (Cloudflare Tunnel)If using Cloudflare Tunnel, ensure Public Hostnames are set to route Auth traffic correctly:your-domain.com/auth* -> http://localhost:8080 (FastAPI)your-domain.com/ -> http://localhost:8501 (Streamlit)