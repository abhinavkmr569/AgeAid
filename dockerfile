# --- SSL CERTIFICATE SETUP INSTRUCTIONS ---
#
# 🍓 FOR RASPBERRY PI (Linux/Docker Host):
# Run these commands in your project folder before building:
#   rm root.crt
#   curl -o root.crt https://letsencrypt.org/certs/isrgrootx1.pem
#   head -n 5 root.crt  <-- Verify it says "-----BEGIN CERTIFICATE-----"
#
# 🖥️ FOR WINDOWS (Local Python Development):
# You must place the certificate in your AppData folder for local scripts to find it.
# PowerShell Command:
#   New-Item -ItemType Directory -Force -Path "$env:APPDATA\postgresql"
#   Invoke-WebRequest -Uri "https://letsencrypt.org/certs/isrgrootx1.pem" -OutFile "$env:APPDATA\postgresql\root.crt"
#
# ------------------------------------------

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Startup: run migrations then launch both services
RUN echo '#!/bin/bash\n\
    echo "Running Database Migrations..."\n\
    alembic upgrade head\n\
    echo "Starting FastAPI..."\n\
    uvicorn main:app --host 0.0.0.0 --port 8080 &\n\
    echo "Starting Streamlit..."\n\
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n\
    ' > start.sh

RUN chmod +x start.sh

EXPOSE 8080
EXPOSE 8501

CMD ["./start.sh"]