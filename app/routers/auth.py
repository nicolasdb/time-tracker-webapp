from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from services import supabase as supabase_service
import json

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

security = HTTPBasic()

# Placeholder for actual auth implementation
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page"""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "auth/login.html", 
        {"request": request, "title": "Login"}
    )

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle login submission"""
    try:
        # Attempt to sign in with Supabase
        response = supabase_service.sign_in(email, password)
        
        # For development, just redirect to dashboard
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        # If login fails, return to login page with error
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/login.html", 
            {
                "request": request, 
                "title": "Login", 
                "error": str(e)
            }
        )

@router.get("/logout")
async def logout():
    """Handle logout"""
    try:
        supabase_service.sign_out(None)  # Token not needed with current implementation
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render the registration page"""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "auth/register.html", 
        {"request": request, "title": "Register"}
    )

@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(None, alias="confirm-password"),
):
    """Handle registration submission"""
    # Validate passwords match
    if confirm_password and password != confirm_password:
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/register.html", 
            {
                "request": request, 
                "title": "Register", 
                "error": "Passwords do not match"
            }
        )
        
    try:
        # Attempt to sign up with Supabase
        user = supabase_service.sign_up(email, password, name)
        
        # For development, redirect to login page with success message
        response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["HX-Trigger"] = json.dumps({"showNotification": "Account created! Check your email to confirm your registration before logging in."})
        return response
    except Exception as e:
        # If registration fails, return to register page with error
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "auth/register.html", 
            {
                "request": request, 
                "title": "Register", 
                "error": str(e)
            }
        )
