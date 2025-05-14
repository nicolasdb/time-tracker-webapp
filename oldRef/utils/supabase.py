"""
Supabase integration for data storage and retrieval.
"""
import os
import logging
import json
from supabase import create_client, Client

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client.
    
    Returns:
        Supabase Client instance or None if configuration is missing
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        logger.warning("Supabase configuration missing")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        return None

def authenticate_service_role() -> Client:
    """
    Initialize a Supabase client with service_role key for bypassing RLS.
    
    Returns:
        Supabase Client instance with service role or None if configuration missing
    """
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not service_key:
        logger.warning("Supabase service role configuration missing")
        return None
    
    try:
        logger.info("Authenticating with service role to bypass RLS...")
        return create_client(url, service_key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client with service role: {str(e)}")
        return None
        
def get_debug_info() -> dict:
    """
    Get debug information about the Supabase configuration.
    
    Returns:
        Dictionary with debug information
    """
    url = os.getenv("SUPABASE_URL", "Not set")
    anon_key_status = "Set" if os.getenv("SUPABASE_KEY") else "Not set"
    service_key_status = "Set" if os.getenv("SUPABASE_SERVICE_KEY") else "Not set"
    
    return {
        "url": url,
        "anon_key": anon_key_status,
        "service_key": service_key_status
    }