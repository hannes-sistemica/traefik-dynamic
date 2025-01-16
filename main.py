from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import uvicorn

app = FastAPI()

# Basic Auth
security = HTTPBasic()

# In-memory configuration
config = {
    "http": {
        "services": {},
        "routers": {},
        "middlewares": {}
    }
}

# Basic Auth dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.getenv("BASIC_AUTH_USERNAME")
    password = os.getenv("BASIC_AUTH_PASSWORD")

    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

@app.get("/config")
def get_config():
    """Endpoint to serve the dynamic configuration to Traefik."""
    return config

@app.post("/upload")
def upload_config(new_config: dict, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """Endpoint to upload and update the dynamic configuration."""
    global config
    config = new_config
    return {"message": "Configuration updated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
