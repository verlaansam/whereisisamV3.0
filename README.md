# Project Description

This project, **whereisisam3**, is designed to track and manage the current location or status of Sam. It provides tools or documentation to help users understand Sam's whereabouts or related information. The purpose and functionality of the project can be extended based on specific requirements.

Feel free to explore and contribute!

# Technical Setup

This project is built using **Django** (backend) and **React** (frontend). Follow the steps below to set up and start the project:

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A virtual environment tool (e.g., `venv` or `virtualenv`)
- Node.js and npm (Node Package Manager)

## Backend Setup (Django)
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/whereisisam3.git
    cd whereisisam3
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

5. Start the development server:
    ```bash
    python manage.py runserver
    ```

6. Open your browser and navigate to `http://127.0.0.1:8000/` to view the backend.

## Frontend Setup (React)
1. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2. Install the required dependencies:
    ```bash
    npm install
    ```

3. Start the React development server:
    ```bash
    npm start
    ```

4. Open your browser and navigate to `http://localhost:3000/` to view the frontend.

## Contributing
Contributions are welcome! Feel free to fork the repository, make changes, and submit a pull request.

For any issues or feature requests, please open an issue in the repository.

Happy coding!

## build local, pull and rund on server

# local:
1) login ghcr
docker login ghcr.io -u verlaansam

2) set tag from commit
TAG=$(git rev-parse --short HEAD)
echo "$TAG"

3) build backend image
docker build \
  -f Dockerfile.prod \
  -t ghcr.io/verlaansam/whereisisam-backend:$TAG \
  -t ghcr.io/verlaansam/whereisisam-backend:latest \
  .
  
4) build frontend image
docker build \
  -f frontend/Dockerfile.prod \
  --build-arg REACT_APP_API_URL=https://whereis.samverlaan.nl/api/ \
  -t ghcr.io/verlaansam/whereisisam-frontend:$TAG \
  -t ghcr.io/verlaansam/whereisisam-frontend:latest \
  ./frontend

5) push images 
docker push ghcr.io/verlaansam/whereisisam-backend:$TAG
docker push ghcr.io/verlaansam/whereisisam-backend:latest
docker push ghcr.io/verlaansam/whereisisam-frontend:$TAG
docker push ghcr.io/verlaansam/whereisisam-frontend:latest


# droplet
cd /opt/whereisisam3
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d