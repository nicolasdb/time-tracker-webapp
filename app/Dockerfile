FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm --version

# # Clone Windster reference repository
# RUN git clone https://github.com/themesberg/tailwind-dashboard-windster.git /tmp/windster \
#     && mkdir -p /app/windster-reference \
#     && cp -r /tmp/windster/* /app/windster-reference/ \
#     && rm -rf /tmp/windster

# clone Flowbite Admin Dashboard
RUN git clone https://github.com/themesberg/flowbite-admin-dashboard.git /tmp/flowbite \
    && mkdir -p /app/flowbite-reference \
    && cp -r /tmp/flowbite/* /app/flowbite-reference/ \
    && rm -rf /tmp/flowbite

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install npm dependencies for Tailwind
COPY package.json .
RUN npm install

# Copy application code - this will be replaced with bind mount in development
COPY . .

# Build Tailwind CSS
RUN npx tailwindcss -i ./static/src/main.css -o ./static/css/main.css

# Expose ports for FastAPI
EXPOSE 8000

# Use CMD to start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
