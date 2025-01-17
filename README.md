# Traefik Config Server

A Python-based service to dynamically update Traefik configuration via HTTP. This project provides a REST API to manage Traefik's dynamic configuration in real-time, allowing you to add, update, or remove services, routers, and middlewares without restarting Traefik.

---

## **Scope**

The `traefik-config-server` is designed to:
1. Serve as a **dynamic configuration provider** for Traefik.
2. Allow **real-time updates** to Traefik's configuration via HTTP.
3. Provide a **secure API** protected with Basic Authentication.
4. Be **lightweight** and **easy to deploy** using Docker.

---

## **Idea**

Traefik is a modern reverse proxy and load balancer that supports dynamic configuration. However, updating Traefik's configuration typically requires modifying configuration files or using external providers like Docker, Kubernetes, or Consul.

This project provides an alternative: a **custom HTTP provider** that allows you to dynamically update Traefik's configuration via a REST API. This is particularly useful for:
- **Custom automation**: Integrate Traefik with your own tools or scripts.
- **Dynamic environments**: Update Traefik's configuration in real-time without restarting.
- **Testing and development**: Quickly test new configurations without modifying files.

---

## **Problem We Came From**

While working with Traefik, we encountered the following challenges:
1. **Static Configuration**: Traefik's configuration files are static and require a restart to apply changes.
2. **Complex Providers**: Using external providers like Docker or Kubernetes can be overkill for simple use cases.
3. **Lack of Flexibility**: There was no easy way to programmatically update Traefik's configuration in real-time.

To solve these issues, we created the `traefik-config-server`, which provides a simple REST API to manage Traefik's dynamic configuration.

---

## **Features**

- **Dynamic Configuration**: Update Traefik's configuration in real-time via HTTP.
- **Web UI**: User-friendly interface for editing and managing configurations.
- **Basic Authentication**: Protect the API with username/password.
- **Lightweight**: Built with Python and FastAPI, designed to run in a Docker container.
- **Easy Integration**: Works seamlessly with Traefik's HTTP provider.

---

## **How to Build, Run, and Use**

### **Prerequisites**
- Docker installed on your machine.
- `curl` or a similar tool for testing the API.

---

### **1. Run the Container**

Start the container using the pre-built image from GitHub Container Registry:

```bash
docker run -d --name traefik-config-server -p 5001:5000 \
  -e BASIC_AUTH_USERNAME=admin \
  -e BASIC_AUTH_PASSWORD=secret \
  ghcr.io/hannes-sistemica/traefik-dynamic:latest
```

---

### **2. Using Docker Compose**

First, set up your environment variables:

```bash
cp example.env .env
```

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  traefik-config:
    image: ghcr.io/hannes-sistemica/traefik-dynamic:latest
    container_name: traefik-config-server
    restart: unless-stopped
    ports:
      - "5001:5000"
    env_file:
      - .env
```

Then start the service:

```bash
docker-compose up -d
```

The server will be available at `http://<your-host>:<port>`.

---

### **3. Use the Web UI**

The configuration server includes a web-based UI for easy configuration management:

1. Access the UI at `http://<your-host>:<port>/ui`
2. Use the Basic Auth credentials (default: admin/secret)
3. Edit the JSON configuration in the text area
4. Click "Save Configuration" to apply changes

The UI provides:
- Real-time configuration editing
- Syntax highlighting for JSON
- Immediate feedback on save success/failure
- Error messages for invalid JSON

### **4. Test the API**

#### Fetch Current Configuration
```bash
curl http://<your-host>:<port>/config
```

#### Upload New Configuration
```bash
curl -u admin:secret -X POST http://<your-host>:<port>/upload \
  -H "Content-Type: application/json" \
  -d '{
    "http": {
      "services": {
        "gitea": {
          "loadBalancer": {
            "servers": [
              {
                "url": "http://192.168.1.2:3000"
              }
            ]
          }
        }
      }
    }
  }'
```

#### Verify Updated Configuration
```bash
curl http://<your-host>:<port>/config
```

---

### **4. Integrate with Traefik**

#### Docker Compose Example

Here's how to configure Traefik with our config server in Docker Compose (this is only an example, make sure to not expose username/passwords!):

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v3.2
    container_name: traefik
    ports:
      - "8081:8080"  # Dashboard
      - "9080:80"    # HTTP
      - "9443:443"   # HTTPS
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command:
      - --api.insecure=true
      - --providers.docker
      - --providers.http.endpoint=http://traefik-config:5000/config
      - --providers.http.pollInterval=10s
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443

  traefik-config:
    image: ghcr.io/hannes-sistemica/traefik-dynamic:latest
    container_name: traefik-config-server
    restart: unless-stopped
    ports:
      - "5001:5000"
    environment:
      - BASIC_AUTH_USERNAME=admin
      - BASIC_AUTH_PASSWORD=secret
```

#### Standalone Traefik Configuration

For a non-Docker setup, add this to your Traefik configuration file:

```yaml
# Enable API and dashboard
api:
  insecure: true
  dashboard: true

# Providers configuration
providers:
  http:
    endpoint: "http://<config-server-ip>:<config-server-port>/config"
    pollInterval: "10s"
  
  file:
    filename: "/etc/traefik/traefik.yml"
    watch: true

# Entry points
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
```

Then start Traefik with:

```bash
traefik --configFile=/etc/traefik/traefik.yml
```

---

### **5. Traefik Polling and Change Detection**

Traefik periodically polls the HTTP provider endpoint to detect configuration changes. Here's how it works:

1. **Polling Mechanism**:
   - Traefik polls the `/config` endpoint at a configurable interval
   - Default polling interval is 30 seconds
   - Configure with `pollInterval` in Traefik's configuration:
     ```yaml
     providers:
       http:
         endpoint: "http://traefik-config-server:5001/config"
         pollInterval: "10s"  # Poll every 10 seconds
     ```

2. **Change Detection**:
   - Traefik compares the new configuration with the current one
   - Changes are applied immediately without restart
   - Invalid configurations are rejected

3. **Example Workflow**:
   - Upload new configuration via `/upload` endpoint
   - Traefik detects changes on next poll
   - New configuration takes effect immediately

4. **Monitoring**:
   - Check Traefik logs for change detection:
     ```
     time="2023-10-10T12:00:00Z" level=info msg="Configuration received from provider: http"
     time="2023-10-10T12:00:00Z" level=info msg="Applying changes for provider: http"
     ```

### **6. Use Makefile (Optional)**

The project includes a `Makefile` for easier management. Here are the available commands:

- **Build the Docker image**:
  ```bash
  make build
  ```

- **Start the container**:
  ```bash
  make start
  ```

- **Stop the container**:
  ```bash
  make stop
  ```

- **Test the API**:
  ```bash
  make test
  ```

- **Clean up resources**:
  ```bash
  make clean
  ```

---

## **Project Structure**

```
traefik-config-server/
├── .dockerignore
├── .env.example
├── .github/
│   └── workflows/
│       └── docker-publish.yml
├── .gitignore
├── Dockerfile
├── Makefile
├── README.md
├── docker-compose.traefik-local.yaml
├── docker-compose.traefik.yaml
├── docker-compose.yml
├── main.py
├── requirements.txt
├── templates/
│   └── index.html
└── traefik-config-example.yml
```

- **`.gitignore`**: Specifies files and directories to ignore in Git.
- **`README.md`**: This file.
- **`Dockerfile`**: Defines the Docker image.
- **`main.py`**: The FastAPI application.
- **`requirements.txt`**: Lists Python dependencies.
- **`Makefile`**: Simplifies building, running, and testing the project.

---

## **API Endpoints**

### **GET `/config`**
- **Description**: Fetch the current configuration.
- **Example**:
  ```bash
  curl -u admin:secret http://localhost:5001/config
  ```

### **POST `/upload`**
- **Description**: Upload a new configuration.
- **Example**:
  ```bash
  curl -u admin:secret -X POST http://localhost:5001/upload \
    -H "Content-Type: application/json" \
    -d '{
      "http": {
        "services": {
          "gitea": {
            "loadBalancer": {
              "servers": [
                {
                  "url": "http://192.168.1.2:3000"
                }
              ]
            }
          }
        }
      }
    }'
  ```

---

## **Environment Variables**

- **`BASIC_AUTH_USERNAME`**: Username for Basic Authentication (default: `admin`).
- **`BASIC_AUTH_PASSWORD`**: Password for Basic Authentication (default: `secret`).

---

## **Contributing**

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Troubleshooting**

### Docker Swarm DNS Resolution

When using Docker Swarm, you might encounter issues where Traefik cannot resolve the `traefik-config` service name. This is because Docker Swarm uses a different DNS resolution pattern.

If Traefik cannot reach `http://traefik-config:5000/config`, try these solutions:

1. **Use the tasks prefix**:
   ```yaml
   services:
     traefik:
       command:
         - --providers.http.endpoint=http://tasks.traefik-config:5000/config
   ```

2. **Use the stack name prefix** (if using a stack):
   ```yaml
   services:
     traefik:
       command:
         - --providers.http.endpoint=http://traefik-config.yourstack:5000/config
   ```

3. **Verify DNS resolution**:
   ```bash
   docker exec -it traefik nslookup traefik-config
   docker exec -it traefik nslookup tasks.traefik-config
   ```

4. **Check network configuration**:
   - Ensure both services are in the same Docker network
   - Verify network connectivity between containers

## **Acknowledgments**

- [Traefik](https://traefik.io/) for being an awesome reverse proxy.
- [FastAPI](https://fastapi.tiangolo.com/) for making it easy to build APIs.
- [Docker](https://www.docker.com/) for simplifying deployment.
