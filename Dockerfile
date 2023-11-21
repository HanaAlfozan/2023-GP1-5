# Use the official Python base image with version 3.11.4
FROM python:3.11.4

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv

# Copy the application code to the container
COPY . .

# Expose a port if your application listens on a specific port
# EXPOSE <port_number>

# Set the command to run when the container starts
CMD ["python", "app.py"]