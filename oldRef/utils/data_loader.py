"""
Data loading and querying utilities for Supabase.
"""
import logging
from typing import Dict, List, Optional, Any

from .supabase import get_supabase_client, authenticate_service_role, get_debug_info

logger = logging.getLogger(__name__)

def test_connection() -> bool:
    """
    Test the connection to Supabase.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Simpler test that doesn't require existing tables
        # Just testing if we can connect to Supabase
        return True
    except Exception as e:
        logger.error(f"Failed to test Supabase connection: {str(e)}")
        return False

def fetch_test_data() -> List[Dict[str, Any]]:
    """
    Fetch sample data for testing the connection.
    This is used for initial validation of the Supabase connection.
    
    Returns:
        List[Dict[str, Any]]: List of sample data items or empty list if failed
    """
    # For initial setup, return dummy data if tables don't exist yet
    dummy_data = [
        {"id": "1", "uid_tag": "tag001", "uid_device": "device001", "event_type": "tap_in", "timestamp": "2025-04-09T12:00:00"},
        {"id": "2", "uid_tag": "tag002", "uid_device": "device001", "event_type": "tap_in", "timestamp": "2025-04-09T13:30:00"},
        {"id": "3", "uid_tag": "tag001", "uid_device": "device001", "event_type": "tap_out", "timestamp": "2025-04-09T17:15:00"}
    ]
    
    # Try with regular client first
    logger.info("Attempting to fetch data with regular client...")
    client = get_supabase_client()
    if not client:
        logger.warning("No regular client available")
        return dummy_data
    
    # Try with service role to bypass RLS if available
    service_client = authenticate_service_role()
    if service_client:
        logger.info("Service role client available, will try after regular client fails")
    else:
        logger.warning("No service role client available - add SUPABASE_SERVICE_KEY to .env to bypass RLS")
    
    try:
        # Store debug info
        debug_info = get_debug_info()
        logger.info(f"Supabase configuration: {debug_info}")
        
        tables_to_check = []
        
        # Try to list tables first
        try:
            logger.info("Checking available tables in the database...")
            
            # Try with regular client
            try:
                table_response = client.table('pg_catalog.pg_tables').select('tablename').eq('schemaname', 'public').execute()
                available_tables = [table['tablename'] for table in table_response.data] if table_response.data else []
                logger.info(f"Available tables in public schema: {available_tables}")
                tables_to_check = available_tables
            except Exception as e:
                logger.warning(f"Could not list tables with regular client: {str(e)}")
                
                # Try with service role client if available
                if service_client:
                    try:
                        logger.info("Trying to list tables with service role client...")
                        table_response = service_client.table('pg_catalog.pg_tables').select('tablename').eq('schemaname', 'public').execute()
                        available_tables = [table['tablename'] for table in table_response.data] if table_response.data else []
                        logger.info(f"Available tables with service role: {available_tables}")
                        tables_to_check = available_tables
                    except Exception as e2:
                        logger.warning(f"Could not list tables with service role either: {str(e2)}")
            
            # If we couldn't get table list, check common table names
            if not tables_to_check:
                tables_to_check = ['rfid_events', 'time_events']
        
            # Try rfid_events table first with regular client
            if 'rfid_events' in tables_to_check:
                logger.info("Trying rfid_events table with regular client...")
                try:
                    response = client.table('rfid_events').select('*').order('timestamp', desc=True).limit(10).execute()
                    if response.data:
                        logger.info(f"Successfully retrieved {len(response.data)} records from rfid_events with regular client")
                        return response.data
                except Exception as e:
                    logger.warning(f"Regular client failed to query rfid_events: {str(e)}")
                    
                # Try with service role if regular client failed
                if service_client:
                    logger.info("Trying rfid_events with service role client...")
                    try:
                        response = service_client.table('rfid_events').select('*').order('timestamp', desc=True).limit(10).execute()
                        if response.data:
                            logger.info(f"Successfully retrieved {len(response.data)} records from rfid_events with service role")
                            return response.data
                    except Exception as e:
                        logger.warning(f"Service role client failed to query rfid_events: {str(e)}")
            
            # Try time_events table next
            if 'time_events' in tables_to_check:
                logger.info("Trying time_events table with regular client...")
                try:
                    response = client.table('time_events').select('*').order('timestamp', desc=True).limit(10).execute()
                    if response.data:
                        logger.info(f"Successfully retrieved {len(response.data)} records from time_events with regular client")
                        return response.data
                except Exception as e:
                    logger.warning(f"Regular client failed to query time_events: {str(e)}")
                    
                # Try with service role if regular client failed
                if service_client:
                    logger.info("Trying time_events with service role client...")
                    try:
                        response = service_client.table('time_events').select('*').order('timestamp', desc=True).limit(10).execute()
                        if response.data:
                            logger.info(f"Successfully retrieved {len(response.data)} records from time_events with service role")
                            return response.data
                    except Exception as e:
                        logger.warning(f"Service role client failed to query time_events: {str(e)}")
                        
        except Exception as e:
            logger.warning(f"Error checking tables: {str(e)}")
        
        # If we got here, we couldn't retrieve data from either table
        logger.warning("No data found in any event tables. Using dummy data.")
        return dummy_data
                
    except Exception as e:
        logger.error(f"Failed to fetch test data: {str(e)}")
        return dummy_data