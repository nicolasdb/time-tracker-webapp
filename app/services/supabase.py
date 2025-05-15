from supabase import create_client
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dnyocxearkrbgiywwplx.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = None

def initialize_supabase():
    """Initialize the Supabase client with credentials."""
    global supabase
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not found in environment variables.")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return False

def get_client():
    """Get the Supabase client. Initialize if not already done."""
    global supabase
    
    if supabase is None:
        initialize_supabase()
    
    return supabase

def check_connection():
    """Check if the Supabase connection is working and if RLS is configured correctly."""
    client = get_client()
    
    if client is None:
        return {
            "status": "error",
            "message": "Supabase client not initialized."
        }
    
    try:
        # Step 1: Basic connectivity check
        try:
            response = client.table("rfid_events").select("count", count="exact").limit(1).execute()
            connectivity_status = "success"
            connectivity_message = "Connected to Supabase."
            rfid_count = response.count
        except Exception as conn_error:
            return {
                "status": "error",
                "message": f"Failed to connect to Supabase: {conn_error}"
            }
            
        # Step 2: Check if the live_board view is accessible
        try:
            view_response = client.from_("live_board").select("count", count="exact").limit(1).execute()
            view_status = "success"
            view_message = "Live Board view is accessible."
            view_count = view_response.count
        except Exception as view_error:
            view_status = "warning"
            view_message = f"Unable to access Live Board view: {view_error}. This may be due to RLS restrictions."
            view_count = 0
            
        # Return comprehensive status
        if view_status == "success":
            return {
                "status": "success",
                "message": f"Connected to Supabase successfully. Live Board view is accessible.",
                "count": view_count,
                "checks": {
                    "connectivity": {"status": connectivity_status, "message": connectivity_message},
                    "view_access": {"status": view_status, "message": view_message}
                }
            }
        else:
            return {
                "status": "warning",
                "message": f"Connected to Supabase but Live Board view is not accessible. Use the /fix-rls endpoint to fix this issue.",
                "count": rfid_count,
                "checks": {
                    "connectivity": {"status": connectivity_status, "message": connectivity_message},
                    "view_access": {"status": view_status, "message": view_message}
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to check connection: {e}")
        return {
            "status": "error",
            "message": f"Failed to check Supabase connection: {e}"
        }

def get_rfid_events(limit=12, offset=0):
    """
    Get RFID events with tag information from the live_board view.
    
    This function uses the correct field names matching your schema:
    - tag_id (not tag_uid)
    - task_name (not tag_name)
    - project_name stays the same
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return []
    
    try:
        # Try to use the live_board view
        try:
            # First check if we can access the view at all
            test_query = client.from_("live_board").select("*").limit(1).execute()
            logger.info(f"Live board view is accessible. Found {len(test_query.data)} records.")
            
            # Now get the actual data
            response = client.from_("live_board").select("*").limit(limit).offset(offset).execute()
            
            events = []
            for event in response.data:
                events.append({
                    "id": event.get("id"),
                    "tag_id": event.get("tag_id"),
                    "task_name": event.get("task_name") or "Unknown",
                    "event_type": event.get("event_type"),
                    "timestamp": event.get("timestamp")
                })
            
            logger.info(f"Successfully retrieved {len(events)} events from live_board view")
            return events
            
        except Exception as view_error:
            logger.warning(f"Failed to query live_board view: {view_error}")
            logger.warning("This may be due to RLS (Row Level Security) restrictions.")
            logger.warning("Try using the /fix-rls endpoint to configure proper permissions.")
            
            # Fallback to direct table query
            try:
                logger.warning("Attempting to fall back to direct rfid_events table query...")
                response = client.from_("rfid_events").select("*").order("timestamp", desc=True).limit(limit).offset(offset).execute()
                
                # Process the results
                events = []
                for event in response.data:
                    events.append({
                        "id": event.get("id"),
                        "tag_id": event.get("tag_id"),
                        "task_name": "Unknown",  # We don't have this info without the view
                        "event_type": event.get("event_type"),
                        "timestamp": event.get("timestamp")
                    })
                
                logger.info(f"Successfully retrieved {len(events)} events from direct rfid_events table")
                return events
            except Exception as table_error:
                logger.error(f"Failed to query rfid_events table: {table_error}")
                return []
            
    except Exception as e:
        logger.error(f"Failed to get RFID events: {e}")
        return []

def get_time_blocks(limit=12, offset=0):
    """
    Get time blocks calculated from RFID events.
    
    This function tries to call the get_time_blocks RPC function.
    If the function is not available, it returns an empty list.
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return []
    
    try:
        # Try to call the get_time_blocks function
        try:
            response = client.rpc(
                "get_time_blocks",
                {"limit_num": limit, "offset_num": offset}
            ).execute()
            
            logger.info(f"Successfully retrieved {len(response.data)} time blocks")
            return response.data
            
        except Exception as func_error:
            logger.warning(f"Failed to call get_time_blocks function: {func_error}. Returning empty list.")
            
            # Since the function is not available, we return an empty list
            # This is a placeholder until the function is created in Supabase
            return []
            
    except Exception as e:
        logger.error(f"Failed to get time blocks: {e}")
        return []

def register_tag(tag_uid, tag_name, project_name=None, user_id=None):
    """
    Register or update a tag in the tag_info table.
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return False
    
    try:
        # Try to insert/update tag info
        try:
            # Check if tag already exists
            existing = client.from_("tag_info").select("*").eq("tag_uid", tag_uid).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing tag
                client.from_("tag_info").update({
                    "tag_name": tag_name,
                    "project_name": project_name,
                    "user_id": user_id,
                    "updated_at": "now()"
                }).eq("tag_uid", tag_uid).execute()
                logger.info(f"Updated tag info for tag_uid: {tag_uid}")
            else:
                # Insert new tag
                client.from_("tag_info").insert({
                    "tag_uid": tag_uid,
                    "tag_name": tag_name,
                    "project_name": project_name,
                    "user_id": user_id
                }).execute()
                logger.info(f"Inserted new tag info for tag_uid: {tag_uid}")
            
            return True
            
        except Exception as tag_error:
            logger.warning(f"Failed to register tag: {tag_error}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to register tag: {e}")
        return False

def get_tag_info(tag_uid):
    """
    Get information about a specific tag.
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return None
    
    try:
        response = client.from_("tag_info").select("*").eq("tag_uid", tag_uid).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get tag info: {e}")
        return None

def get_all_tags(limit=100, offset=0):
    """
    Get all registered tags.
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return []
    
    try:
        response = client.from_("tag_info").select("*").order("tag_name").limit(limit).offset(offset).execute()
        return response.data
    except Exception as e:
        logger.error(f"Failed to get tags: {e}")
        return []

def execute_sql(query):
    """
    Execute raw SQL directly. Use with caution!
    
    This function is intended for administrative tasks only,
    such as setting up views and permissions.
    
    WARNING: Using this with user input could lead to SQL injection!
    """
    client = get_client()
    
    if client is None:
        logger.error("Supabase client not initialized.")
        return {"status": "error", "message": "Supabase client not initialized."}
    
    try:
        # Try to use the RPC method if available
        try:
            response = client.rpc("execute_sql", {"query": query}).execute()
            logger.info("SQL executed successfully using RPC")
            return {"status": "success", "message": "SQL executed successfully."}
        except Exception as rpc_error:
            logger.warning(f"Failed to execute SQL with RPC: {rpc_error}")
            logger.warning("This likely means you need to use a service role key with higher privileges.")
            return {"status": "error", "message": f"Failed to execute SQL: {rpc_error}"}
            
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        return {"status": "error", "message": f"Failed to execute SQL: {e}"}

# Initialize Supabase when the module is imported
initialize_supabase()
