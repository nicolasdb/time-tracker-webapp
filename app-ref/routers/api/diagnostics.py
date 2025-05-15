from fastapi import APIRouter, Request, Depends, HTTPException
from services import supabase as supabase_service
import logging

router = APIRouter(
    tags=["diagnostics"],
)

logger = logging.getLogger(__name__)

@router.get("/diagnostics")
async def get_diagnostics():
    """
    Run diagnostics on system components and return status
    """
    try:
        # Check Supabase connection
        supabase_connection = False
        api_status = True  # Assume API is online since we're responding
        
        # Table record counts
        table_counts = {
            "tag_assignments": 0,
            "rfid_events": 0,
            "time_blocks": 0,
            "device_assignments": 0
        }
        
        # If Supabase client is initialized
        if hasattr(supabase_service, 'supabase') and supabase_service.supabase:
            try:
                # Test connection by querying a small amount of data
                tag_response = supabase_service.supabase.table('tag_assignments').select('count', count='exact').limit(1).execute()
                supabase_connection = True
                
                # Get table counts
                if tag_response.count is not None:
                    table_counts["tag_assignments"] = tag_response.count
                
                events_response = supabase_service.supabase.table('rfid_events').select('count', count='exact').limit(1).execute()
                if events_response.count is not None:
                    table_counts["rfid_events"] = events_response.count
                
                time_blocks_response = supabase_service.supabase.table('time_blocks').select('count', count='exact').limit(1).execute()
                if time_blocks_response.count is not None:
                    table_counts["time_blocks"] = time_blocks_response.count
                
                devices_response = supabase_service.supabase.table('device_assignments').select('count', count='exact').limit(1).execute()
                if devices_response.count is not None:
                    table_counts["device_assignments"] = devices_response.count
                
            except Exception as e:
                logger.error(f"Error connecting to Supabase: {str(e)}")
                supabase_connection = False
        
        # Return diagnostics results
        return {
            "supabase_connection": supabase_connection,
            "api_status": api_status,
            "table_counts": table_counts,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error running diagnostics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diagnostics failed: {str(e)}")
