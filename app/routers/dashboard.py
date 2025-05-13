from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard"""
    templates = request.app.state.templates
    
    # Placeholder data - will be replaced with real data from Supabase
    mock_data = {
        "total_hours_today": 6.5,
        "total_hours_week": 32.5,
        "tags_count": 15,
        "projects": [
            {"name": "Project A", "hours": 12.5, "percentage": 38},
            {"name": "Project B", "hours": 8.3, "percentage": 26},
            {"name": "Project C", "hours": 6.2, "percentage": 19},
            {"name": "Other", "hours": 5.5, "percentage": 17}
        ],
        "recent_activities": [
            {"project": "Project A", "duration": "2h 15m", "timestamp": "Today, 10:30 AM"},
            {"project": "Project B", "duration": "1h 30m", "timestamp": "Today, 2:00 PM"},
            {"project": "Project C", "duration": "45m", "timestamp": "Yesterday, 4:15 PM"}
        ]
    }
    
    return templates.TemplateResponse(
        "dashboard/index.html", 
        {"request": request, "title": "Dashboard", "data": mock_data}
    )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    """Render the analytics page"""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "dashboard/analytics.html", 
        {"request": request, "title": "Analytics"}
    )
