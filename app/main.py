from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import platform

# Create the FastAPI app
app = FastAPI(
    title="Time Tracker Journey",
    description="Time tracking application with NFC tags",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Store templates in app state for access in routers
app.state.templates = templates

@app.get("/")
async def home(request: Request):
    """Home page with diagnostic information"""
    # System information
    system_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "os": platform.system(),
        "hostname": platform.node(),
        "processor": platform.processor()
    }
    
    # Environment variables
    env_vars = {key: value for key, value in os.environ.items() if not key.startswith("_")}
    
    # Installed packages
    try:
        import pkg_resources
        packages = sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set])
    except:
        packages = ["Could not retrieve package information"]
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "System Diagnostics",
            "system_info": system_info,
            "env_vars": env_vars,
            "packages": packages
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/ui")
async def ui_components(request: Request):
    """UI components showcase"""
    return templates.TemplateResponse(
        "ui_components.html",
        {
            "request": request,
            "title": "UI Components"
        }
    )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
