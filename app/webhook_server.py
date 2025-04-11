"""
Webhook server for the Time Tracker application.
Handles device events and stores them in Supabase.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List, Union, Any

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from dotenv import load_dotenv
from utils.supabase import get_supabase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Time Tracker Webhook",
    description="API for receiving and processing device events",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Define models
class DeviceEvent(BaseModel):
    """Model for device events."""
    timestamp: str = Field(..., description="Event timestamp in ISO format")
    event_type: str = Field(..., description="Event type: tag_insert or tag_removed")
    tag_present: bool = Field(..., description="Whether tag is present")
    tag_id: str = Field(..., description="RFID tag ID")
    tag_type: Optional[str] = Field(None, description="Type of RFID tag")
    wifi_status: Optional[str] = Field(None, description="WiFi connection status")
    time_status: Optional[str] = Field(None, description="Time synchronization status")
    device_id: str = Field(..., description="Device ID")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = ['tag_insert', 'tag_removed']
        if v not in allowed_types:
            raise ValueError(f"event_type must be one of {allowed_types}")
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("timestamp must be in ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "ok"
    version: str = "0.1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Authentication functions
async def verify_api_key(request: Request, api_key: str = Depends(api_key_header)) -> Dict:
    """
    Verify the API key against registered device keys.
    Supports both X-API-Key header and Bearer token in Authorization header.
    
    Args:
        request: The FastAPI request object
        api_key: The API key from the X-API-Key header
        
    Returns:
        Dict with device information
        
    Raises:
        HTTPException: If API key is invalid
    """
    # Log all headers for debugging
    headers = dict(request.headers.items())
    safe_headers = {k: v if k.lower() not in ('authorization', 'x-api-key') else f"{v[:5]}..." for k, v in headers.items()}
    logger.info(f"Request headers: {safe_headers}")
    
    # First try to get from Authorization header (Bearer token)
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        logger.info("Found Bearer token in Authorization header")
        api_key = authorization.replace("Bearer ", "")
    elif api_key:
        logger.info("Using API key from X-API-Key header")
    else:
        logger.info("No API key found in headers")
    
    if not api_key:
        logger.warning("Authentication failed: API key is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    
    # Get Supabase clients - try both regular and service role
    from utils.supabase import authenticate_service_role
    
    supabase = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Use service client if available, otherwise use regular client
    client_to_use = service_client if service_client else supabase
    client_type = "service role" if service_client else "regular"
    
    if not client_to_use:
        logger.error("Failed to get any Supabase client")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    
    try:
        # Log the API key prefix we're searching for
        logger.info(f"Searching for API key: {api_key[:5]}... using {client_type} client")
        
        # Query device_keys table
        response = client_to_use.table("device_keys").select("*").eq("api_key", api_key).execute()
        
        # Log response for debugging (sanitized)
        logger.info(f"API key search response data length: {len(response.data) if response.data else 0}")
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"Invalid API key attempt: {api_key[:5]}...")
            
            # Try to debug with a broader search
            try:
                # Check if any keys exist at all
                all_keys = supabase.table("device_keys").select("count").execute()
                key_count = all_keys.count if hasattr(all_keys, 'count') else "unknown"
                logger.info(f"Total keys in database: {key_count}")
            except Exception as count_error:
                logger.error(f"Error counting keys: {str(count_error)}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        
        device_key = response.data[0]
        # Log success with safe values
        logger.info(f"API key {api_key[:5]}... verified for device: {device_key['device_id']}")
        return device_key
    
    except Exception as e:
        logger.error(f"API key verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying API key",
        )

# API endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.get("/api/webhook/validate-key")
async def validate_api_key(request: Request, device_key: Dict = Depends(verify_api_key)):
    """
    Validate the API key without sending an event.
    Use this endpoint to test if your API key is working correctly.
    
    Args:
        request: The FastAPI request object
        device_key: The verified device key data from Depends
    
    Returns:
        JSON with validation status
    """
    # If we got here, the API key is valid
    return {
        "status": "success",
        "message": "API key is valid",
        "device_id": device_key.get("device_id", "unknown"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/webhook/device-event")
async def receive_device_event(
    event: DeviceEvent,
    device_key: Dict = Depends(verify_api_key)
):
    """
    Receive and process device events.
    
    Args:
        event: The device event data
        device_key: The verified device key data
        
    Returns:
        JSON response with status
    """
    # Log the incoming event data (sanitized)
    logger.info(f"Received device event: type={event.event_type}, device={event.device_id}, tag={event.tag_id}")
    logger.info(f"Authenticated with key for device: {device_key['device_id']}")
    
    # Verify device ID matches the API key's device
    if event.device_id != device_key["device_id"]:
        logger.warning(f"Device ID mismatch: {event.device_id} vs {device_key['device_id']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device ID does not match API key",
        )
    
    # Get Supabase clients - try both regular and service role
    from utils.supabase import authenticate_service_role
    
    supabase = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Use service client if available, otherwise use regular client
    client_to_use = service_client if service_client else supabase
    client_type = "service role" if service_client else "regular"
    
    if not client_to_use:
        logger.error("Failed to get any Supabase client")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
    
    try:
        # Store event in database
        event_data = event.dict()
        
        logger.info(f"Storing event using {client_type} client")
        
        # Insert event
        response = client_to_use.table("rfid_events").insert(event_data).execute()
        
        if not response.data:
            logger.error("Failed to insert event")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store event",
            )
        
        logger.info(f"Event stored: {event.event_type} for tag {event.tag_id}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status": "success", "message": "Event stored successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing event: {str(e)}",
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with custom format."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"}
    )

if __name__ == "__main__":
    # Run the server directly when script is executed
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    
    logger.info(f"Starting webhook server on {host}:{port}")
    uvicorn.run("webhook_server:app", host=host, port=port, reload=True)