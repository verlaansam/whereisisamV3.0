#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_GHCR_USER="verlaansam"
DEFAULT_API_URL="https://whereis.samverlaan.nl/api/"

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
}

require_command git
require_command docker

cd "$ROOT_DIR"

DEFAULT_TAG="$(git rev-parse --short HEAD)"
TAG="${TAG:-$DEFAULT_TAG}"
GHCR_USER="$DEFAULT_GHCR_USER"
REACT_APP_API_URL="$DEFAULT_API_URL"

echo
echo "Release configuration"
echo "  GHCR user: $GHCR_USER"
echo "  Tag: $TAG"
echo "  Frontend API URL: $REACT_APP_API_URL"
echo

read -r -s -p "GHCR token: " GHCR_PASSWORD
echo

if [[ -z "$GHCR_PASSWORD" ]]; then
  echo "GHCR token is required." >&2
  exit 1
fi

printf '%s' "$GHCR_PASSWORD" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

unset GHCR_PASSWORD

docker build \
  -f Dockerfile.prod \
  -t "ghcr.io/verlaansam/whereisisam-backend:$TAG" \
  -t "ghcr.io/verlaansam/whereisisam-backend:latest" \
  .

docker build \
  -f frontend/Dockerfile.prod \
  --build-arg "REACT_APP_API_URL=$REACT_APP_API_URL" \
  -t "ghcr.io/verlaansam/whereisisam-frontend:$TAG" \
  -t "ghcr.io/verlaansam/whereisisam-frontend:latest" \
  ./frontend

docker push "ghcr.io/verlaansam/whereisisam-backend:$TAG"
docker push "ghcr.io/verlaansam/whereisisam-backend:latest"

docker push "ghcr.io/verlaansam/whereisisam-frontend:$TAG"
docker push "ghcr.io/verlaansam/whereisisam-frontend:latest"

echo
echo "Done."
