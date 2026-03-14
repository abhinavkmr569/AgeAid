FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create startup script
RUN printf '#!/bin/bash\n\
echo "⏳ Waiting for database to be ready..."\n\
until pg_isready -h db -p 5432 -U healthuser; do\n\
  echo "   Postgres not ready, retrying in 2s..."\n\
  sleep 2\n\
done\n\
echo "✅ Database is ready!"\n\
\n\
echo "🔄 Running Database Migrations..."\n\
alembic upgrade heads\n\

\n\
echo "🚀 Starting FastAPI..."\n\
uvicorn main:app --host 0.0.0.0 --port 8502 &\n\
\n\
echo "🎨 Starting Streamlit..."\n\
streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n\
' > start.sh

RUN chmod +x start.sh

EXPOSE 8502
EXPOSE 8501

CMD ["./start.sh"]