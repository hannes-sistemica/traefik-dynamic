# Variables
IMAGE_NAME = traefik-config-server
CONTAINER_NAME = traefik-config-server
PORT = 5001
USERNAME = admin
PASSWORD = secret

# Start the containers
start:
	@echo "Starting services with docker-compose..."
	docker-compose up -d
	@echo "Services are running. Traefik dashboard available at http://localhost:8080"

# Stop the containers
stop:
	@echo "Stopping services..."
	docker-compose down
	@echo "Services stopped and removed."

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

# Help message
help:
	@echo "Available commands:"
	@echo "  make start    - Start the container"
	@echo "  make stop     - Stop the container"
	@echo "  make test     - Test upload/download functionality"
	@echo "  make build    - Build the Docker image"
	@echo "  make clean    - Clean up Docker resources"
	@echo "  make help     - Show this help message"

.PHONY: start stop test build clean help
