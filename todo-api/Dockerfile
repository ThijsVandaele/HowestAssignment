# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (required for MariaDB client and others)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the wait-for-it script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Copy the requirements.txt into the container
COPY requirements.txt /app/

# Install Python dependencies from the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire FastAPI app code into the container
COPY ./src /app/

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Start the app only after MariaDB is ready, using the dynamic DB_HOST environment variable
CMD ["/wait-for-it.sh", "todo-mariadb:3306", "--timeout=60", "--strict", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]