"""
Time tracking component for the time tracker application.
"""
import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from utils.supabase import get_supabase_client, authenticate_service_role

logger = logging.getLogger(__name__)

def fetch_recent_events(days: int = 2) -> List[Dict[str, Any]]:
    """
    Fetch recent RFID events from Supabase.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of event dictionaries or empty list if no data
    """
    client = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Use service client if available, otherwise regular client
    supabase = service_client if service_client else client
    
    if not supabase:
        logger.error("No Supabase client available")
        return []
    
    try:
        # Query the rfid_events table for recent events
        response = supabase.table('rfid_events').select('*') \
            .gte('timestamp', start_date.isoformat()) \
            .order('timestamp', desc=False) \
            .execute()
        
        if response.data:
            logger.info(f"Retrieved {len(response.data)} recent events")
            return response.data
        
        logger.warning("No recent events found")
        return []
    except Exception as e:
        logger.error(f"Failed to fetch recent events: {str(e)}")
        return []

def fetch_time_blocks(days: int = 2) -> List[Dict[str, Any]]:
    """
    Fetch time blocks from the time_blocks view in Supabase.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of time block dictionaries or empty list if no data
    """
    client = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Use service client if available, otherwise regular client
    supabase = service_client if service_client else client
    
    if not supabase:
        logger.error("No Supabase client available")
        return []
    
    try:
        # Query the time_blocks view for recent blocks
        response = supabase.table('time_blocks').select('*') \
            .gte('start_time', start_date.isoformat()) \
            .order('start_time', desc=False) \
            .execute()
        
        if response.data:
            logger.info(f"Retrieved {len(response.data)} time blocks")
            return response.data
        
        logger.warning("No time blocks found")
        return []
    except Exception as e:
        logger.error(f"Failed to fetch time blocks: {str(e)}")
        return []

def format_duration(minutes: float) -> str:
    """
    Format duration in minutes to a readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted string like "2h 30m"
    """
    if pd.isna(minutes):
        return ""
    
    hours, mins = divmod(int(minutes), 60)
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def get_tag_info(tag_id: str, tags_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get tag information from the tag assignments data.
    
    Args:
        tag_id: The tag ID to look up
        tags_data: List of tag assignment data
        
    Returns:
        Dictionary with tag information or empty dict if not found
    """
    for tag in tags_data:
        if tag.get('tag_id') == tag_id:
            return tag
    return {}

def fetch_tag_assignments() -> List[Dict[str, Any]]:
    """
    Fetch all tag assignments from Supabase.
    
    Returns:
        List of tag assignment dictionaries or empty list if no data
    """
    client = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Use service client if available, otherwise regular client
    supabase = service_client if service_client else client
    
    if not supabase:
        logger.error("No Supabase client available")
        return []
    
    try:
        response = supabase.table('tag_assignments').select('*').execute()
        if response.data:
            logger.info(f"Retrieved {len(response.data)} tag assignments")
            return response.data
        return []
    except Exception as e:
        logger.error(f"Failed to fetch tag assignments: {str(e)}")
        return []

def get_dashboard_metrics() -> Dict[str, Any]:
    """
    Get metrics for the dashboard.
    
    Returns:
        Dictionary with metrics:
        - active_projects: Number of unique projects with time logged in last 7 days
        - total_tags: Number of tags in the system
        - total_devices: Number of devices in the system
        - today_time: Minutes tracked today
        - week_time: Minutes tracked in the last 7 days
        - completed_tasks: Count of tasks with at least 1 time block in the last 7 days
    """
    metrics = {
        'active_projects': 0,
        'total_tags': 0, 
        'total_devices': 0,
        'today_time': 0,
        'week_time': 0,
        'completed_tasks': 0
    }
    
    try:
        # Get time blocks for the last 7 days
        time_blocks = fetch_time_blocks(days=7)
        if time_blocks:
            df = pd.DataFrame(time_blocks)
            
            # Convert timestamps
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['activity_date'] = pd.to_datetime(df['activity_date']).dt.date
            
            # Get today
            today = datetime.now().date()
            
            # Active projects (unique project names in last 7 days)
            active_projects = df['project_name'].dropna().unique()
            metrics['active_projects'] = len(active_projects)
            
            # Today's time
            today_df = df[df['activity_date'] == today]
            metrics['today_time'] = today_df['duration_minutes'].sum() if not today_df.empty else 0
            
            # Week time
            metrics['week_time'] = df['duration_minutes'].sum()
            
            # Completed tasks (unique project+task combinations)
            task_combinations = df.dropna(subset=['project_name', 'task_name']).apply(
                lambda x: f"{x['project_name']}/{x['task_name']}", axis=1
            ).unique()
            metrics['completed_tasks'] = len(task_combinations)
        
        # Get tag count
        tags = fetch_tag_assignments()
        metrics['total_tags'] = len(tags) if tags else 0
        
        # Get device count
        client = get_supabase_client()
        service_client = authenticate_service_role()
        supabase = service_client if service_client else client
        
        if supabase:
            try:
                response = supabase.table('device_assignments').select('*').execute()
                if response.data:
                    # Filter out NULL device_ids
                    valid_devices = [d for d in response.data if d.get('device_id')]
                    metrics['total_devices'] = len(valid_devices)
            except Exception as e:
                logger.error(f"Failed to fetch device count: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error calculating dashboard metrics: {str(e)}")
    
    return metrics

def display_time_tracking():
    """
    Display the time tracking interface with raw events and time blocks.
    """
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Daily Time Blocks", "Raw RFID Events"])
    
    # Fetch the necessary data
    with st.spinner("Loading time tracking data..."):
        # Get tag assignments for lookup
        tag_assignments = fetch_tag_assignments()
        
        # Get time blocks for yesterday and today
        time_blocks = fetch_time_blocks(days=2)
        
        # Get raw events for yesterday and today
        events = fetch_recent_events(days=2)
    
    with tab1:
        st.markdown("### Time Blocks")
        
        if not time_blocks:
            st.info("No time blocks found for the last 2 days. Try scanning some tags!")
        else:
            # Convert to dataframe
            df = pd.DataFrame(time_blocks)
            
            # Convert timestamp strings to datetime objects
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
            df['activity_date'] = pd.to_datetime(df['activity_date']).dt.date
            
            # Get today and yesterday dates
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Format the duration column
            df['formatted_duration'] = df['duration_minutes'].apply(format_duration)
            
            # Create two sections: Today and Yesterday
            st.markdown("#### Today's Activities")
            today_blocks = df[df['activity_date'] == today].copy()
            
            if today_blocks.empty:
                st.info("No activities recorded today.")
            else:
                # Calculate total time for today
                total_minutes = today_blocks['duration_minutes'].sum()
                st.metric("Total time tracked today", format_duration(total_minutes))
                
                # Format for display
                display_df = today_blocks.copy()
                
                # Format timestamps for display
                display_df['Start'] = display_df['start_time'].dt.strftime('%H:%M')
                display_df['End'] = display_df['end_time'].dt.strftime('%H:%M')
                display_df['Duration'] = display_df['formatted_duration']
                
                # Add category and name
                display_df['Project'] = display_df['project_name']
                display_df['Task'] = display_df['task_name']
                
                # Select and order columns for display
                display_cols = ['Start', 'End', 'Duration', 'Project', 'Task', 'tag_id']
                final_df = display_df[display_cols].rename(columns={'tag_id': 'Tag ID'})
                
                # Display the dataframe
                st.dataframe(final_df, use_container_width=True)
            
            st.markdown("#### Yesterday's Activities")
            yesterday_blocks = df[df['activity_date'] == yesterday].copy()
            
            if yesterday_blocks.empty:
                st.info("No activities recorded yesterday.")
            else:
                # Calculate total time for yesterday
                total_minutes = yesterday_blocks['duration_minutes'].sum()
                st.metric("Total time tracked yesterday", format_duration(total_minutes))
                
                # Format for display
                display_df = yesterday_blocks.copy()
                
                # Format timestamps for display
                display_df['Start'] = display_df['start_time'].dt.strftime('%H:%M')
                display_df['End'] = display_df['end_time'].dt.strftime('%H:%M')
                display_df['Duration'] = display_df['formatted_duration']
                
                # Add category and name
                display_df['Project'] = display_df['project_name']
                display_df['Task'] = display_df['task_name']
                
                # Select and order columns for display
                display_cols = ['Start', 'End', 'Duration', 'Project', 'Task', 'tag_id']
                final_df = display_df[display_cols].rename(columns={'tag_id': 'Tag ID'})
                
                # Display the dataframe
                st.dataframe(final_df, use_container_width=True)
            
            # Show total time tracked in the last two days
            st.divider()
            total_minutes = df['duration_minutes'].sum()
            st.metric("Total time tracked (last 2 days)", format_duration(total_minutes))
    
    with tab2:
        st.markdown("### Raw RFID Events")
        
        if not events:
            st.info("No RFID events found for the last 2 days.")
        else:
            # Convert to dataframe
            df = pd.DataFrame(events)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Add a date column
            df['date'] = df['timestamp'].dt.date
            
            # Get today and yesterday dates
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Create two sections: Today and Yesterday
            st.markdown("#### Today's Events")
            today_events = df[df['date'] == today].copy()
            
            if today_events.empty:
                st.info("No events recorded today.")
            else:
                # Format for display
                display_df = today_events.copy()
                
                # Format timestamp for display
                display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
                
                # Event type and tag present
                display_df['Event'] = display_df['event_type'].apply(lambda x: "Insert" if x == "tag_insert" else "Remove")
                display_df['Present'] = display_df['tag_present'].apply(lambda x: "Yes" if x else "No")
                
                # Get tag information if available
                display_df['Tag Info'] = display_df['tag_id'].apply(
                    lambda x: next((f"{t.get('project_name', '')}/{t.get('task_name', '')}" 
                                  for t in tag_assignments if t.get('tag_id') == x), "")
                )
                
                # Select and order columns for display
                display_cols = ['Time', 'Event', 'tag_id', 'Tag Info', 'Present', 'device_id']
                renamed_cols = {
                    'tag_id': 'Tag ID',
                    'device_id': 'Device ID'
                }
                final_df = display_df[display_cols].rename(columns=renamed_cols)
                
                # Display the dataframe
                st.dataframe(final_df, use_container_width=True)
            
            st.markdown("#### Yesterday's Events")
            yesterday_events = df[df['date'] == yesterday].copy()
            
            if yesterday_events.empty:
                st.info("No events recorded yesterday.")
            else:
                # Format for display
                display_df = yesterday_events.copy()
                
                # Format timestamp for display
                display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
                
                # Event type and tag present
                display_df['Event'] = display_df['event_type'].apply(lambda x: "Insert" if x == "tag_insert" else "Remove")
                display_df['Present'] = display_df['tag_present'].apply(lambda x: "Yes" if x else "No")
                
                # Get tag information if available
                display_df['Tag Info'] = display_df['tag_id'].apply(
                    lambda x: next((f"{t.get('project_name', '')}/{t.get('task_name', '')}" 
                                  for t in tag_assignments if t.get('tag_id') == x), "")
                )
                
                # Select and order columns for display
                display_cols = ['Time', 'Event', 'tag_id', 'Tag Info', 'Present', 'device_id']
                renamed_cols = {
                    'tag_id': 'Tag ID',
                    'device_id': 'Device ID'
                }
                final_df = display_df[display_cols].rename(columns=renamed_cols)
                
                # Display the dataframe
                st.dataframe(final_df, use_container_width=True)
            
            # Show total events in the last two days
            st.divider()
            st.metric("Total RFID events (last 2 days)", len(df))