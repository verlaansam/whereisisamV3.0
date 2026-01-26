# Backend Dockerfile - Django
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (from venv)
COPY ./env/whereissam/whereissam/settings.py .
COPY ./env/whereissam/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project files
COPY ./env/whereissam/manage.py .
COPY ./env/whereissam/whereissam ./whereissam
COPY ./env/whereissam/core ./core

# Create directories for media and static files
RUN mkdir -p /app/media /app/staticfiles

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
