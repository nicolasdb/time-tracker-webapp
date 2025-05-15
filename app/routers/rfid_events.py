from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from services import supabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rfid-events",
    tags=["rfid_events"],
)

async def get_events_data(page: int = 1, limit: int = 12):
    """Get data for RFID events page, to be used by both /rfid-events and homepage"""
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get RFID events from Supabase using live_board view
    try:
        events = supabase.get_rfid_events(limit=limit, offset=offset)
        
        # Disabled time blocks for now
        time_blocks = []
        active_session = None
        
        # Get connection status
        connection_status = supabase.check_connection()
        
        # Calculate pagination
        total_count = connection_status.get("count", 0) if connection_status.get("status") == "success" else 0
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        
        return {
            "events": events,
            "time_blocks": time_blocks,
            "active_session": active_session,
            "connection_status": connection_status,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": total_pages
            }
        }
    except Exception as e:
        logger.error(f"Error fetching RFID events: {e}")
        return {
            "events": [],
            "time_blocks": [],
            "active_session": None,
            "connection_status": {
                "status": "error",
                "message": f"Failed to fetch RFID events: {str(e)}"
            },
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 1
            }
        }

@router.get("/", response_class=HTMLResponse)
async def list_events(
    request: Request,
    page: int = 1,
    limit: int = 12
):
    """Render the RFID events page showing all events from the live_board view."""
    templates = request.app.state.templates
    
    # Get events data
    events_data = await get_events_data(page=page, limit=limit)
    
    return templates.TemplateResponse(
        "index.html",  # Updated to use the new template name
        {
            "request": request,
            "title": "RFID Live Board",
            **events_data
        }
    )

@router.get("/check-connection")
async def check_supabase_connection():
    """Check the Supabase connection status."""
    return supabase.check_connection()

@router.post("/fix-rls")
async def fix_rls():
    """
    Fix RLS issues for the live_board view using correct field names,
    and implement column-level security for sensitive fields.
    """
    try:
        # Step 1: Create or replace the live_board view with correct field names
        view_result = supabase.execute_sql("""
        DROP VIEW IF EXISTS public.live_board;

        CREATE VIEW public.live_board AS
        SELECT 
            e.id,
            e.event_type,
            e.timestamp,
            e.tag_id,
            t.task_name
        FROM rfid_events e
        LEFT JOIN tag_assignments t ON e.tag_id = t.tag_id
        ORDER BY e.timestamp DESC;
        """)
        
        if view_result["status"] != "success":
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to create live_board view."}
            )
        
        # Step 2: Enable RLS on the underlying tables
        rls_result = supabase.execute_sql("""
        ALTER TABLE rfid_events ENABLE ROW LEVEL SECURITY;
        ALTER TABLE tag_assignments ENABLE ROW LEVEL SECURITY;
        """)
        
        if rls_result["status"] != "success":
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to enable RLS on tables."}
            )
        
        # Step 3: Create policies to allow anonymous access
        policy_result = supabase.execute_sql("""
        -- Create policies for anonymous read access
        DROP POLICY IF EXISTS "Allow anonymous read access to rfid_events" ON rfid_events;
        CREATE POLICY "Allow anonymous read access to rfid_events" ON rfid_events
            FOR SELECT
            TO anon
            USING (true);

        DROP POLICY IF EXISTS "Allow anonymous read access to tag_assignments" ON tag_assignments;
        CREATE POLICY "Allow anonymous read access to tag_assignments" ON tag_assignments
            FOR SELECT
            TO anon
            USING (true);
        """)
        
        if policy_result["status"] != "success":
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to create RLS policies."}
            )
        
        # Step 4: Implement column-level security
        column_security_result = supabase.execute_sql("""
        -- First, revoke all privileges on the table from the anon role
        REVOKE ALL ON tag_assignments FROM anon;

        -- Grant access to only specific columns
        GRANT SELECT (tag_id, task_name) ON tag_assignments TO anon;

        -- For the rfid_events table
        REVOKE ALL ON rfid_events FROM anon;
        GRANT SELECT (id, event_type, timestamp, tag_id) ON rfid_events TO anon;
        """)
        
        if column_security_result["status"] != "success":
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to set up column-level security."}
            )
        
        # Step 5: Grant permissions to the view
        grant_result = supabase.execute_sql("""
        GRANT SELECT ON live_board TO anon;
        """)
        
        if grant_result["status"] != "success":
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to grant permissions to the view."}
            )
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Successfully set up RLS and column-level security.",
                "details": "Created live_board view with restricted column access."
            }
        )
    except Exception as e:
        logger.error(f"Error fixing RLS: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Failed to fix RLS: {str(e)}"}
        )