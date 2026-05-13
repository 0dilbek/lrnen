# Deployment Guide

This project is prepared for deployment using Docker and Docker Compose.

## Prerequisites
- Docker
- Docker Compose

## Steps to Deploy

1. **Environment Variables**
   Copy `.env.example` to `.env` and fill in the values:
   ```bash
   cp .env.example .env
   ```
   Make sure to set `DEBUG=False` and provide a strong `SECRET_KEY`.

2. **Build and Start**
   Run the following command to build the images and start the containers:
   ```bash
   docker-compose up --build -d
   ```

3. **Database Migrations**
   Run migrations inside the backend container:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

4. **Create Superuser**
   Create an admin account:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

## Architecture
- **Frontend**: React (Vite) built and served by Nginx on port 80.
- **Backend**: Django (Gunicorn) running on port 8000.
- **Reverse Proxy**: Nginx (inside the frontend container) routes `/api`, `/static`, and `/media` to the backend.

## Static & Media Files
- Static files are collected automatically during the build process.
- Media files (uploaded images/audio) are stored in a persistent Docker volume.
