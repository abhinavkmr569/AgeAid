# 1. Use Python 3.11 (Stable)
FROM python:3.11-slim

WORKDIR /app

# 2. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy All Code
COPY . .

# 4. EXPLICITLY Copy Cert to App Folder
COPY root.crt /app/root.crt

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

# 5. Place it where Postgres expects it & Fix Permissions
# This is the critical block that was broken
RUN mkdir -p /root/.postgresql && \
    cp /app/root.crt /root/.postgresql/root.crt && \
    chmod 600 /root/.postgresql/root.crt

# 6. Startup Script
RUN echo '#!/bin/bash\n\
    echo "Running Database Migrations..."\n\
    alembic upgrade head\n\
    echo "Starting Services..."\n\
    uvicorn main:app --host 0.0.0.0 --port 8080 & \n\
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n\
    ' > start.sh

# 7. Permissions & Ports
RUN chmod +x start.sh
EXPOSE 8080
EXPOSE 8501

# 8. Run
CMD ["./start.sh"]