# Use the official Python base image with version 3.11.4
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .
# Copy the application code to the container
COPY . .

# Combine apt-get update, install dependencies, and clean up in a single RUN command
# Install apt dependencies
RUN set -e \
    && apt-get update \
    && apt-get install -y python3-opencv postgresql-client libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN set -e \
    && pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

# Expose a port if your application listens on a specific port
# EXPOSE <port_number>

# Set the command to run when the container starts
CMD ["python", "app.py"]
