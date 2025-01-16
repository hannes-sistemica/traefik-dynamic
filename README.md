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
- **Basic Authentication**: Protect the API with username/password.
- **Lightweight**: Built with Python and FastAPI, designed to run in a Docker container.
- **Easy Integration**: Works seamlessly with Traefik's HTTP provider.

---

## **How to Build, Run, and Use**

### **Prerequisites**
- Docker installed on your machine.
- `curl` or a similar tool for testing the API.

---

### **1. Build the Docker Image**

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-username/traefik-config-server.git
cd traefik-config-server
```

Build the Docker image:

```bash
docker build -t traefik-config-server .
```

---

### **2. Run the Container**

Start the container:

```bash
docker run -d --name traefik-config-server -p 5001:5001 \
  -e BASIC_AUTH_USERNAME=admin \
  -e BASIC_AUTH_PASSWORD=secret \
  traefik-config-server
```

The server will be available at `http://localhost:5001`.

---

### **3. Test the API**

#### Fetch Current Configuration
```bash
curl -u admin:secret http://localhost:5001/config
```

#### Upload New Configuration
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
                "url": "http://192.168.1.251:3000"
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
curl -u admin:secret http://localhost:5001/config
```

---

### **4. Integrate with Traefik**

Update your Traefik configuration to use the `traefik-config-server` as an HTTP provider:

```yaml
providers:
  http:
    endpoint: "http://traefik-config-server:5001/config"
```

---

### **5. Use Makefile (Optional)**

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
├── .gitignore
├── README.md
├── Dockerfile
├── main.py
├── requirements.txt
└── Makefile
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
                  "url": "http://192.168.1.251:3000"
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

## **Acknowledgments**

- [Traefik](https://traefik.io/) for being an awesome reverse proxy.
- [FastAPI](https://fastapi.tiangolo.com/) for making it easy to build APIs.
- [Docker](https://www.docker.com/) for simplifying deployment.
