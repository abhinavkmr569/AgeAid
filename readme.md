# Health Trend Tracker (SaaS):

A personal health dashboard that uses AI to extract data from PDF/Image blood reports, standardizes test results, and visualizes long-term health trends with a "Universal Health Score".<-- Replace with a screenshot of your app🚀 FeaturesAI-Powered Extraction: Uses Google Gemini 2.5 Flash to read data from any blood report format (PDF, JPG, PNG).Universal Normalization: Automatically maps different test names (e.g., "Fasting Sugar" vs. "Fasting Glucose") to a single standard ID using fuzzy logic.Health Score (0-100): Converts raw values into a percentage score based on the specific reference range of that report, solving the problem of different labs using different scales.Holistic Analysis: Uses Gemini 2.5 Pro to analyze trends across entire body systems (e.g., Kidney Function) while considering your lifestyle (Diet, Sleep, Activity).Timeline Visualization: Plots trends over time with dynamic charts that handle date formats intelligently.Privacy-First: Self-hostable on a Raspberry Pi or scalable on Google Cloud Run.🏗️ Tech StackComponentTechnologyPurposeFrontendStreamlitThe user interface (Dashboard, Charts, Uploads).BackendFastAPIHigh-performance API for handling logic and database calls.AI EngineGoogle Gemini 2.5Flash for fast extraction, Pro for deep reasoning.DatabaseCockroachDB ServerlessPostgreSQL-compatible database with a generous free tier.DeploymentDockerContainerizes the entire stack for easy deployment anywhere.📂 File Structurehealth_backend/
├── app.py               # Frontend: Streamlit UI Logic
├── main.py              # Backend: FastAPI Server Logic
├── extractor.py         # AI: Gemini Prompt Engineering & Logic
├── database.py          # DB: Connection handling (CockroachDB)
├── models.py            # DB: SQLAlchemy Table Definitions
├── schemas.py           # API: Pydantic Data Validation Models
├── clusters.py          # Logic: Grouping tests (e.g., "Kidney Function")
├── normalizer.py        # Logic: Fuzzy matching for test names
├── utils.py             # Helper: Date parsing & formatting
├── reset_db.py          # Utility: Wipes database for schema updates
├── requirements.txt     # Dependencies list
├── Dockerfile           # Deployment configuration
└── .env                 # Secrets (API Keys & DB URL)
⚡ Quick Start (Local Deployment)1. PrerequisitesDocker Desktop installed and running.A Google Gemini API Key (Get it from Google AI Studio).A CockroachDB Serverless Cluster (Get it from CockroachDB Cloud).2. SetupClone the repository:git clone [https://github.com/YOUR_USERNAME/health-trend-tracker.git](https://github.com/YOUR_USERNAME/health-trend-tracker.git)
cd health-trend-tracker
Create the .env file:Create a file named .env in the root folder and add your keys:GEMINI_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://user:password@host:26257/healthdb?sslmode=verify-full
Download SSL Certificate (Windows Only):Open PowerShell and run the command provided by CockroachDB to download the root.crt certificate to your AppData folder.3. Run with DockerThis single command builds the container and starts both the Backend and Frontend.# Build the image
docker build -t health-app .

# Run the container (Windows PowerShell)
docker run -d --name health-server -p 8080:8080 -p 8501:8501 --env-file .env -v $env:APPDATA\postgresql:/root/.postgresql health-app

# Run the container (Mac/Linux)
# Note: You may need to download the cert to the project folder first
docker run -d --name health-server -p 8080:8080 -p 8501:8501 --env-file .env health-app
4. Access the AppFrontend: Open http://localhost:8501 in your browser.Backend Docs: http://localhost:8080/docs🌍 Deployment (Google Cloud Run)This project is designed to run 100% Free on Google Cloud Run's free tier.Install Google Cloud SDK and login:gcloud auth login
gcloud config set project YOUR_PROJECT_ID
Deploy Command:gcloud run deploy health-app \
  --source . \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --port 8501 \
  --set-env-vars "GEMINI_API_KEY=your_key,DATABASE_URL=your_db_url"
Done! You will get a public URL (e.g., https://health-app.a.run.app) to share with users.🛠️ Maintenance & UpdatesUpdating the Database SchemaIf you add new columns to models.py (e.g., new lifestyle factors), you must update the database structure.Option A: Hard Reset (Data Loss)For early development only. Wipes all users and reports.docker exec health-server python reset_db.py
docker restart health-server
Option B: Migration (Production Safe)Use Alembic (configured in the repo) to apply changes safely.alembic revision --autogenerate -m "Added new column"
alembic upgrade head
📝 LicenseMIT License