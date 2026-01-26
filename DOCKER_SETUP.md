# Docker Setup Guide for WhereIsSam3

## Files Created

I've created the following Docker configuration files:

1. **Dockerfile** (root) - Backend Django container
2. **frontend/Dockerfile** - React frontend container
3. **docker-compose.yml** - Orchestrates both services
4. **.dockerignore** files - Exclude unnecessary files from build context
5. **requirements.txt** - Python dependencies

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to project root
cd /home/sam/Documents/whereisisam3

# Build and start all services
docker-compose up --build

# The services will be available at:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:3000
```

### Option 2: Individual Container Commands

```bash
# Build backend
docker build -t whereissam-backend .

# Build frontend
docker build -t whereissam-frontend ./frontend

# Run backend
docker run -p 8000:8000 \
  -v $(pwd)/env/whereissam/media:/app/media \
  whereissam-backend

# Run frontend
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  whereissam-frontend
```

## Detailed Architecture

### Backend (Django)
- **Image**: python:3.12-slim
- **Port**: 8000
- **Volumes**: 
  - `./env/whereissam/media:/app/media` - Persists uploaded files
  - `./env/whereissam/db.sqlite3:/app/db.sqlite3` - Persists database
- **Features**:
  - Automatically runs migrations on startup
  - Serves at 0.0.0.0:8000 for container access

### Frontend (React)
- **Image**: node:20-alpine (multi-stage build)
- **Port**: 3000
- **Build Process**: 
  - Stage 1: Builds optimized production bundle
  - Stage 2: Serves with `serve` package for production-ready environment
- **Environment**: REACT_APP_API_URL points to backend

## Common Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs backend        # Backend logs
docker-compose logs frontend       # Frontend logs
docker-compose logs -f            # Follow all logs

# Stop services
docker-compose stop

# Remove containers and networks
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Run one-off commands
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell
```

## Development vs Production

### Current Setup (Development)
- DEBUG = True
- SQLite database
- Media files stored locally
- Auto-migration on startup

### For Production, Update:

1. **django-compose.yml** - Change environment and commands
2. **Django settings.py** - Set DEBUG=False, ALLOWED_HOSTS
3. Use PostgreSQL instead of SQLite
4. Add SSL/HTTPS
5. Use nginx/traefik for reverse proxy

Example production Dockerfile addition:
```dockerfile
ENV DEBUG=False
ENV ALLOWED_HOSTS=yourdomain.com
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Or kill existing process:
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend
```

### CORS Errors
Ensure Django's CORS settings in `settings.py` include:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### React Can't Connect to Backend
Check that `REACT_APP_API_URL` environment variable is set correctly in docker-compose.yml

### Database Issues
```bash
# Fresh start with clean database
docker-compose down -v
docker-compose up --build
```

## Notes

- The backend uses Django's development server. For production, use Gunicorn.
- The frontend uses `serve` package for production-ready serving
- Both containers are on the same network for internal communication
- Media files and database are mounted as volumes for persistence

