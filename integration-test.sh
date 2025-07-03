#!/bin/bash
set -euo pipefail

COMPOSE_FILE="integration-test-compose.yaml"
ENGINE="podman"

# Parse optional argument for engine
if [[ $# -gt 0 ]]; then
  if [[ "$1" == "docker" ]]; then
    ENGINE="docker"
  elif [[ "$1" == "podman" ]]; then
    ENGINE="podman"
  else
    echo "Usage: $0 [docker|podman]"
    exit 1
  fi
fi

# Use an array for the compose command for safety
COMPOSE_CMD=("$ENGINE" compose -f "$COMPOSE_FILE")

# Build all images
"${COMPOSE_CMD[@]}" build

# Start postgres in detached mode
"${COMPOSE_CMD[@]}" up -d glvd-postgres

# Wait for postgres to be healthy
echo "Waiting for glvd-postgres to be healthy..."
until "${COMPOSE_CMD[@]}" exec -T glvd-postgres pg_isready -U glvd -d glvd; do
  sleep 2
done

# Run ingestion (waits for completion)
"${COMPOSE_CMD[@]}" up --no-deps --abort-on-container-exit --exit-code-from ingestion ingestion
INGESTION_EXIT_CODE=$?

if [ $INGESTION_EXIT_CODE -ne 0 ]; then
  echo "Ingestion failed, skipping assert and shutting down."
  "${COMPOSE_CMD[@]}" down
  exit $INGESTION_EXIT_CODE
fi

# Run assert (waits for completion)
"${COMPOSE_CMD[@]}" up --no-deps --abort-on-container-exit --exit-code-from assert assert
ASSERT_EXIT_CODE=$?

# Shut everything down
"${COMPOSE_CMD[@]}" down

exit $ASSERT_EXIT_CODE
