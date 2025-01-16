from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import uvicorn
import json

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Basic Auth
security = HTTPBasic()

import os
from pathlib import Path

CONFIG_FILE = "/data/config.json"

# Load initial configuration
def load_config():
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "http": {
            "services": {},
            "routers": {},
            "middlewares": {}
        }
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# Initialize config
config = load_config()

# Basic Auth dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.environ["BASIC_AUTH_USERNAME"]
    password = os.environ["BASIC_AUTH_PASSWORD"]

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
    credentials: HTTPBasicCredentials = Depends(authenticate)
):
    """Handle configuration updates from the UI."""
    global config
    
    # Log incoming request headers
    print("Incoming request headers:", request.headers)
    
    form_data = await request.form()
    print("Form data received:", form_data)
    
    # Try both field names for backward compatibility
    config_data = form_data.get("config_data") or form_data.get("config")
    print("Config data received:", config_data)
    
    if not config_data:
        print("No config_data found in form submission")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "config": json.dumps(config, indent=2),
                "message": "No configuration data provided!",
                "success": False
            },
            status_code=400
        )
    
    try:
        new_config = json.loads(config_data)
        save_config(new_config)
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
                "config": config_data,  # Return the raw input for debugging
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
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host=host, port=port)
