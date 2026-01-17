# Use official Python runtime as base image
FROM python:3.10-slim

# Set the locale to UTF-8 (THIS FIXES YOUR ENCODING ISSUE!)
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
# Force Python to use UTF-8 for IO
ENV PYTHONIOENCODING=utf-8

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]