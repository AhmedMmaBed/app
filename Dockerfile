FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HR_DATA_DIR=/app/data
ENV PYTHONUNBUFFERED=1

# Expose the ports for the web app (5000) and ADMS server (8081)
EXPOSE 5000
EXPOSE 8081

# Create the data directory (volume mount point)
RUN mkdir -p /app/data

# Use a shell script as entrypoint to run multiple processes if needed, 
# or just the main Flask app. Here we use an entrypoint script or just run python.
# For simplicity, we run the web application directly. 
# To run background sync tasks, it's recommended to run a separate container or use supervisord.
CMD ["python", "app.py"]
