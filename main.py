from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import uvicorn
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

@app.get("/ui", response_class=HTMLResponse)
def config_ui(request: Request, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """Serve the configuration editor UI."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "config": json.dumps(config, indent=2)
        }
    )

@app.post("/ui/config", response_class=HTMLResponse)
async def update_config_ui(
    request: Request,
    config_data: str = Form(...),
    credentials: HTTPBasicCredentials = Depends(authenticate)
):
    """Handle configuration updates from the UI."""
    try:
        new_config = json.loads(config_data)
        global config
        config = new_config
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "config": json.dumps(config, indent=2),
                "message": "Configuration updated successfully!",
                "success": True
            }
        )
    except json.JSONDecodeError:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "config": config,
                "message": "Invalid JSON format!",
                "success": False
            },
            status_code=400
        )

@app.post("/upload")
def upload_config(new_config: dict, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """Endpoint to upload and update the dynamic configuration."""
    global config
    config = new_config
    return {"message": "Configuration updated successfully"}

@app.get("/health")
def health_check():
    """Health check endpoint for container monitoring."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
