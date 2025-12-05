# Dockerfile
# Use a Python image that matches your current version (or a modern one like 3.11/3.10)
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies first (for better caching)
# CRITICAL: If you don't have a requirements.txt, create it now using:
# pip freeze > requirements.txt
COPY financial_news_intel/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project code into the container
COPY . .

# The command to run when the container starts (we won't use this directly in tests, 
# but it's good practice for running the main app later)
CMD ["sleep", "infinity"]