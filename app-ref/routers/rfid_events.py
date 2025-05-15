from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/rfid-events",
    tags=["rfid_events"],
)

@router.get("/", response_class=HTMLResponse)
async def list_events(
    request: Request,
    page: int = 1,
    limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tag_uid: Optional[str] = None
):
    """Render the RFID events listing page"""
    templates = request.app.state.templates
    
    # Placeholder data - will be replaced with real data from Supabase
    mock_events = [
        {
            "id": 1, 
            "tag_uid": "04A2B3C4", 
            "event_type": "placed", 
            "timestamp": "2025-05-13T09:30:00Z",
            "tag_name": "Work",
            "project": "Project A"
        },
        {
            "id": 2, 
            "tag_uid": "04A2B3C4", 
            "event_type": "removed", 
            "timestamp": "2025-05-13T12:45:00Z",
            "tag_name": "Work",
            "project": "Project A"
        },
        {
            "id": 3, 
            "tag_uid": "15B3C4D5", 
            "event_type": "placed", 
            "timestamp": "2025-05-13T13:15:00Z",
            "tag_name": "Study",
            "project": "Project B"
        },
        {
            "id": 4, 
            "tag_uid": "15B3C4D5", 
            "event_type": "removed", 
            "timestamp": "2025-05-13T15:30:00Z",
            "tag_name": "Study",
            "project": "Project B"
        },
    ]
    
    # Filter parameters that would be applied to the actual data
    filters = {
        "page": page,
        "limit": limit,
        "start_date": start_date,
        "end_date": end_date,
        "tag_uid": tag_uid
    }
    
    # Pagination info
    pagination = {
        "page": page,
        "limit": limit,
        "total": 100,  # Mock total count
        "pages": 5     # Mock total pages
    }
    
    return templates.TemplateResponse(
        "rfid_events/index.html", 
        {
            "request": request, 
            "title": "RFID Events", 
            "events": mock_events,
            "filters": filters,
            "pagination": pagination
        }
    )

@router.get("/create", response_class=HTMLResponse)
async def create_event_form(request: Request):
    """Render the manual event creation form"""
    templates = request.app.state.templates
    
    # Mock tags for dropdown
    mock_tags = [
        {"uid": "04A2B3C4", "name": "Work"},
        {"uid": "15B3C4D5", "name": "Study"},
        {"uid": "26C4D5E6", "name": "Exercise"},
        {"uid": "37D5E6F7", "name": "Reading"},
    ]
    
    return templates.TemplateResponse(
        "rfid_events/create.html", 
        {"request": request, "title": "Create RFID Event", "tags": mock_tags}
    )

@router.post("/create")
async def create_event(
    request: Request,
    tag_uid: str = Form(...),
    event_type: str = Form(...),
    timestamp: datetime = Form(...)
):
    """Handle manual event creation"""
    # This will be implemented with real event creation logic
    # For now, just redirect back to the events list
    return RedirectResponse(url="/rfid-events", status_code=303)

@router.get("/{event_id}/edit", response_class=HTMLResponse)
async def edit_event_form(request: Request, event_id: int):
    """Render the event edit form"""
    templates = request.app.state.templates
    
    # Placeholder data - will be replaced with real data from Supabase
    event = {
        "id": event_id, 
        "tag_uid": "04A2B3C4", 
        "event_type": "placed", 
        "timestamp": "2025-05-13T09:30:00",
        "tag_name": "Work",
        "project": "Project A"
    }
    
    # Mock tags for dropdown
    mock_tags = [
        {"uid": "04A2B3C4", "name": "Work"},
        {"uid": "15B3C4D5", "name": "Study"},
        {"uid": "26C4D5E6", "name": "Exercise"},
        {"uid": "37D5E6F7", "name": "Reading"},
    ]
    
    return templates.TemplateResponse(
        "rfid_events/edit.html", 
        {
            "request": request, 
            "title": "Edit RFID Event", 
            "event": event,
            "tags": mock_tags
        }
    )

@router.post("/{event_id}/edit")
async def edit_event(
    request: Request,
    event_id: int,
    tag_uid: str = Form(...),
    event_type: str = Form(...),
    timestamp: datetime = Form(...)
):
    """Handle event update"""
    # This will be implemented with real event update logic
    # For now, just redirect back to the events list
    return RedirectResponse(url="/rfid-events", status_code=303)

@router.post("/{event_id}/delete")
async def delete_event(request: Request, event_id: int):
    """Handle event deletion"""
    # This will be implemented with real event deletion logic
    # For now, just redirect back to the events list
    return RedirectResponse(url="/rfid-events", status_code=303)
