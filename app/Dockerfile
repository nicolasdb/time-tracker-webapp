FROM python:3.11-slim

WORKDIR /app

# Install only the essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - this will be replaced with bind mount in development
COPY . .

# Expose ports for FastAPI
EXPOSE 8000

# Use CMD to start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
