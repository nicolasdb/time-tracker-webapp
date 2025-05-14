from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

from routers import auth, dashboard, tags, rfid_events
from routers.api import router as api_router

app = FastAPI(
    title="Time Tracker Journey",
    description="A FastAPI application for tracking time and managing tags",
    version="1.0.0"
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
app.state.templates = templates

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)  # Remove the prefix here since it's already in the router
app.include_router(tags.router)
app.include_router(rfid_events.router)
app.include_router(api_router)

# Direct diagnostics endpoint for testing
@app.get("/diagnostics")
async def root_diagnostics():
    """Root-level diagnostics endpoint"""
    return {
        "status": "ok",
        "message": "Root diagnostics endpoint working", 
        "supabase_connection": False,
        "api_status": True,
        "table_counts": {
            "tag_assignments": '?',
            "rfid_events": '?',
            "time_blocks": '?',
            "device_assignments": '?'
        }
    }

@app.get("/")
async def root(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Time Tracker Journey"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/settings")
async def settings(request: Request):
    """Render the settings page"""
    return templates.TemplateResponse(
        "settings.html", 
        {"request": request, "title": "Settings"}
    )

@app.get("/reflections")
async def reflections(request: Request):
    """Render the reflections page"""
    return templates.TemplateResponse(
        "reflections.html", 
        {"request": request, "title": "Reflections"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
