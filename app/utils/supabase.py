"""
Supabase integration for data storage and retrieval.
"""
import os
import logging
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