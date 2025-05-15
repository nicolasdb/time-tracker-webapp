from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)

@router.get("/", response_class=HTMLResponse)
async def list_tags(request: Request):
    """Render the tags listing page"""
    templates = request.app.state.templates
    
    # Placeholder data - will be replaced with real data from Supabase
    mock_tags = [
        {"id": 1, "uid": "04A2B3C4", "name": "Work", "color": "bg-blue-500", "project": "Project A"},
        {"id": 2, "uid": "15B3C4D5", "name": "Study", "color": "bg-green-500", "project": "Project B"},
        {"id": 3, "uid": "26C4D5E6", "name": "Exercise", "color": "bg-red-500", "project": "Project C"},
        {"id": 4, "uid": "37D5E6F7", "name": "Reading", "color": "bg-yellow-500", "project": "Project D"},
    ]
    
    return templates.TemplateResponse(
        "tags/index.html", 
        {"request": request, "title": "Tag Management", "tags": mock_tags}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_tag_form(request: Request):
    """Render the tag creation form"""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "tags/create.html", 
        {"request": request, "title": "Create Tag"}
    )

@router.post("/create")
async def create_tag(
    request: Request,
    name: str = Form(...),
    uid: str = Form(...),
    project: str = Form(...),
    color: str = Form(...)
):
    """Handle tag creation"""
    # This will be implemented with real tag creation logic
    # For now, just redirect back to the tags list
    return RedirectResponse(url="/tags", status_code=303)

@router.get("/{tag_id}/edit", response_class=HTMLResponse)
async def edit_tag_form(request: Request, tag_id: int):
    """Render the tag edit form"""
    templates = request.app.state.templates
    
    # Placeholder data - will be replaced with real data from Supabase
    tag = {"id": tag_id, "uid": f"{tag_id}A2B3C4", "name": f"Tag {tag_id}", "color": "bg-blue-500", "project": f"Project {tag_id}"}
    
    return templates.TemplateResponse(
        "tags/edit.html", 
        {"request": request, "title": "Edit Tag", "tag": tag}
    )

@router.post("/{tag_id}/edit")
async def edit_tag(
    request: Request,
    tag_id: int,
    name: str = Form(...),
    project: str = Form(...),
    color: str = Form(...)
):
    """Handle tag update"""
    # This will be implemented with real tag update logic
    # For now, just redirect back to the tags list
    return RedirectResponse(url="/tags", status_code=303)

@router.post("/{tag_id}/delete")
async def delete_tag(request: Request, tag_id: int):
    """Handle tag deletion"""
    # This will be implemented with real tag deletion logic
    # For now, just redirect back to the tags list
    return RedirectResponse(url="/tags", status_code=303)
