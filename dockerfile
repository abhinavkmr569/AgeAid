# 1. Use Python 3.11 (Stable)
FROM python:3.11-slim

WORKDIR /app

# 2. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy All Code (main.py, app.py, extractor.py, etc.)
COPY . .

# 4. Create a startup script to run both servers
# We create this file inside the container to avoid Windows line-ending issues
RUN echo '#!/bin/bash\n\
    uvicorn main:app --host 0.0.0.0 --port 8080 & \n\
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n\
    ' > start.sh

# 5. Make the script executable
RUN chmod +x start.sh

# 6. Expose Ports (8080 for API, 8501 for UI)
EXPOSE 8080
EXPOSE 8501

# 7. Run the script
CMD ["./start.sh"]