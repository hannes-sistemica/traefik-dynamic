# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app
RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Copy application code
COPY --chown=appuser . .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# Add container metadata
LABEL org.opencontainers.image.source="https://github.com/hannes-sistemica/traefik-dynamic"
LABEL org.opencontainers.image.description="Traefik Config Server"
LABEL org.opencontainers.image.licenses="MIT"

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
