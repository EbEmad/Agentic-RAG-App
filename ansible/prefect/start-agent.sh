#!/bin/bash
set -e

echo "Waiting for Prefect Orion API at $PREFECT_API_URL..."
until curl -s --fail "$PREFECT_API_URL/health"; do
  echo "Orion not ready yet. Retrying in 5s..."
  sleep 5
done

echo "Creating default-agent-pool work pool (if it does not exist)..."
if prefect work-pool create default-agent-pool --type process; then
  echo "Work pool created."
else
  echo "Work pool probably already exists, continuing..."
fi

echo "Orion is up. Starting Prefect agent..."
prefect agent start -p default-agent-pool
