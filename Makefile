# ------------------------------
# Predictive Maintenance MLOps - Makefile
# ------------------------------
# Notes:
# 1. Prefect agent container already includes the dataset (from `data-storage` branch),
#    so peer reviewers don't need MinIO or S3.
# 2. Docker must be installed on the host, and Jenkins must be run in a container with
#    access to the host's Docker daemon.
# 3. The Docker group ID (usually 999 on Linux hosts) MUST be the same inside Jenkins
#    for `docker exec` to work.

# ------------------------------
# Setup Jenkins (one-time, for host)
# ------------------------------
# To start Jenkins (with Docker access):
# 1. Find the Docker group ID on host: `getent group docker`
#    - It usually looks like: docker:x:999:
# 2. Start Jenkins, mounting the Docker socket and matching the group ID:
#    (Replace 999 with your actual group ID)
#    docker run -d \
#      --name jenkins \
#      -p 8080:8080 -p 50000:50000 \
#      -v jenkins_home:/var/jenkins_home \
#      -v /var/run/docker.sock:/var/run/docker.sock \
#      --group-add 999 \
#      jenkins/jenkins:lts

# ------------------------------
# Environment Setup
# ------------------------------

# Set up virtual environment and install dependencies (for local runs)
setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	pre-commit install || true  # Optional, skips if pre-commit not configured

# ------------------------------
# Code Quality (used by Jenkins CI)
# ------------------------------
lint:
	black --check src tests
	flake8 src tests

# ------------------------------
# Unit + Integration Tests
# ------------------------------
test:
	pytest --maxfail=1 --disable-warnings -q

# ------------------------------
# Training Pipeline (Prefect)
# ------------------------------
# Runs the registered Prefect deployment (requires Prefect agent running locally).
train:
	docker exec prefect-prefect-agent-1 prefect deployment run 'Bearing Failure Prediction Pipeline/deployment-pipeline'


# ------------------------------
# FastAPI Service (Local Testing)
# ------------------------------
deploy:
	uvicorn src.api:app --host 0.0.0.0 --port 8000

# ------------------------------
# Build & Run FastAPI API in Docker
# ------------------------------
docker-build:
	docker build -t predictive-api .

docker-run:
	docker run -p 8000:8000 predictive-api

# ------------------------------
# Clean Cache & Reports
# ------------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf .pytest_cache reports/*.html
