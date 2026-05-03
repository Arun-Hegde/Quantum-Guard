# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 5000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcap2-bin \
    libpcap-dev \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY quantumguard/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Create empty __init__.py if it doesn't exist to make it a package
RUN touch quantumguard/__init__.py

# Expose the port
EXPOSE 5000

# Run the application with gunicorn
# We use --bind 0.0.0.0:$PORT to support Render's dynamic port assignment
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 quantumguard.api.app:app
