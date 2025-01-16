# Variables
IMAGE_NAME = ghcr.io/hannes-sistemica/traefik-dynamic
CONTAINER_NAME = traefik-config-server
PORT = 5001
USERNAME = admin
PASSWORD = secret

# Start the container
start:
	@echo "Starting $(CONTAINER_NAME)..."
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):5000 \
		-e BASIC_AUTH_USERNAME=$(USERNAME) \
		-e BASIC_AUTH_PASSWORD=$(PASSWORD) \
		$(IMAGE_NAME)
	@echo "$(CONTAINER_NAME) is running."
	@echo "API: http://localhost:$(PORT)/config"
	@echo "UI: http://localhost:$(PORT)/ui"

# Stop the container
stop:
	@echo "Stopping $(CONTAINER_NAME)..."
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	@echo "$(CONTAINER_NAME) stopped and removed."

# Test upload and download functionality
test:
	@echo "Testing upload and download functionality..."
	@echo "Fetching current configuration..."
	@curl -u $(USERNAME):$(PASSWORD) -s http://localhost:5001/config | jq
	@echo "Uploading configuration from traefik-config-example.yml..."
	@curl -u $(USERNAME):$(PASSWORD) -X POST http://localhost:5001/upload \
		-H "Content-Type: application/json" \
		-d @traefik-config-example.yml | jq
	@echo "Fetching updated configuration..."
	@curl -u $(USERNAME):$(PASSWORD) -s http://localhost:5001/config | jq
	@echo "Testing health check..."
	@curl -s http://localhost:5001/health | jq
	@echo "Test complete."

# Build the Docker image
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) .
	@echo "Docker image built."

# Clean up project-specific Docker resources
clean:
	@echo "Cleaning up project-specific Docker resources..."
	@docker stop $(CONTAINER_NAME) || true
	@docker rm $(CONTAINER_NAME) || true
	@docker rmi $(IMAGE_NAME) || true
	@echo "Project-specific Docker resources cleaned."

# Start Traefik with config server
start-traefik:
	@echo "Starting Traefik with config server..."
	docker-compose -f docker-compose.traefik.yaml up -d
	@echo "Traefik dashboard: http://traefik.localhost:8081"
	@echo "Config server: http://config.localhost:9080"

# Stop and clean Traefik compose setup
stop-traefik:
	@echo "Stopping and cleaning Traefik compose setup..."
	docker-compose -f docker-compose.traefik.yaml down -v
	@echo "Traefik compose setup stopped and volumes removed."

# Run locally with uv
run:
	@echo "Installing dependencies and starting server with uv..."
	@uv pip install -r requirements.txt
	@uvicorn main:app --host 0.0.0.0 --port 5000 --reload

# Help message
help:
	@echo "Available commands:"
	@echo "  make start         - Start the container"
	@echo "  make start-traefik - Start Traefik with config server"
	@echo "  make stop          - Stop the container"
	@echo "  make stop-traefik  - Stop Traefik compose and clean volumes"
	@echo "  make test          - Test upload/download functionality"
	@echo "  make build         - Build the Docker image"
	@echo "  make clean         - Clean up Docker resources"
	@echo "  make run           - Run locally with uv (development)"
	@echo "  make help          - Show this help message"

.PHONY: start stop test build clean help
