"""
Device management component for the time tracker application.
"""
import logging
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional

from utils.supabase import get_supabase_client, authenticate_service_role

logger = logging.getLogger(__name__)

def fetch_all_devices() -> List[Dict[str, Any]]:
    """
    Fetch all device assignments from Supabase.
    
    Returns:
        List of device assignment dictionaries or empty list if no data
    """
    client = get_supabase_client()
    
    # First try with regular client
    if client:
        try:
            response = client.table('device_assignments').select('*').order('assigned_at', desc=True).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} devices with regular client")
                return response.data
        except Exception as e:
            logger.warning(f"Failed to fetch devices with regular client: {str(e)}")
    
    # Try with service role if regular client failed
    service_client = authenticate_service_role()
    if service_client:
        try:
            response = service_client.table('device_assignments').select('*').order('assigned_at', desc=True).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} devices with service role client")
                return response.data
        except Exception as e:
            logger.warning(f"Failed to fetch devices with service role client: {str(e)}")
    
    # Return empty list if all attempts failed
    return []

def create_update_device(device_data: Dict[str, Any], device_id: Optional[str] = None) -> bool:
    """
    Create or update a device assignment in Supabase.
    
    Args:
        device_data: Dictionary with device data fields
        device_id: Optional device_id for update operations
    
    Returns:
        bool: True if successful, False otherwise
    """
    client = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Use service client if available, otherwise regular client
    supabase = service_client if service_client else client
    
    if not supabase:
        logger.error("No Supabase client available")
        return False
    
    try:
        # Get the current user ID for device ownership
        from utils.auth import get_current_user_id
        user_id = get_current_user_id()
        
        # Add user_id to device data if we have one
        if user_id and 'user_id' not in device_data:
            device_data['user_id'] = user_id
            logger.info(f"Adding user_id {user_id} to device data")
        
        if device_id:
            # Update existing device
            response = supabase.table('device_assignments').update(device_data).eq('device_id', device_id).execute()
            if response.data:
                logger.info(f"Updated device: {device_id}")
                return True
        else:
            # Create new device
            response = supabase.table('device_assignments').insert(device_data).execute()
            if response.data:
                logger.info(f"Created new device: {device_data['device_id']} for user: {device_data.get('user_id', 'None')}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to {'update' if device_id else 'create'} device: {str(e)}")
        return False

def delete_device(device_id: str) -> bool:
    """
    Delete a device assignment from Supabase.
    
    Args:
        device_id: ID of the device to delete
    
    Returns:
        bool: True if successful, False otherwise
    """
    client = get_supabase_client()
    service_client = authenticate_service_role()
    
    # Use service client if available, otherwise regular client
    supabase = service_client if service_client else client
    
    if not supabase:
        logger.error("No Supabase client available")
        return False
    
    try:
        response = supabase.table('device_assignments').delete().eq('device_id', device_id).execute()
        if response:
            logger.info(f"Deleted device: {device_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to delete device: {str(e)}")
        return False

def display_device_management():
    """
    Display the device management interface with CRUD operations.
    """
    # Header removed to avoid duplication with page title
    
    # Initialize state variables if they don't exist
    if 'devices' not in st.session_state:
        st.session_state.devices = fetch_all_devices()
    
    if 'edit_device' not in st.session_state:
        st.session_state.edit_device = None
    
    if 'device_filter' not in st.session_state:
        st.session_state.device_filter = ""
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Device List", "Add/Edit Device"])
    
    with tab1:
        # Add refresh button and search/filter
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Refresh", key="refresh_devices"):
                st.session_state.devices = fetch_all_devices()
                st.success("Device list refreshed!")
        
        with col2:
            st.session_state.device_filter = st.text_input(
                "🔍 Search devices",
                value=st.session_state.device_filter,
                placeholder="Filter by device ID or name..."
            )
        
        # Display device list
        if not st.session_state.devices:
            st.info("No devices found. Add a new device using the 'Add/Edit Device' tab.")
        else:
            # Convert to dataframe for display
            df = pd.DataFrame(st.session_state.devices)
            
            # Apply filter if specified
            if st.session_state.device_filter:
                filter_term = st.session_state.device_filter.lower()
                filter_mask = df['device_id'].astype(str).str.lower().str.contains(filter_term)
                
                if 'device_name' in df.columns:
                    name_mask = df['device_name'].fillna('').astype(str).str.lower().str.contains(filter_term)
                    filter_mask = filter_mask | name_mask
                
                if 'location' in df.columns:
                    location_mask = df['location'].fillna('').astype(str).str.lower().str.contains(filter_term)
                    filter_mask = filter_mask | location_mask
                
                df = df[filter_mask]
            
            # Format the dataframe for display
            display_df = df.copy()
            
            # Rename columns for better display
            column_renames = {
                'device_id': 'Device ID',
                'device_name': 'Device Name',
                'location': 'Location',
                'notes': 'Notes',
                'assigned_at': 'Assigned At'
            }
            display_df = display_df.rename(columns={k: v for k, v in column_renames.items() if k in display_df.columns})
            
            # Format date columns for better readability
            if 'Assigned At' in display_df.columns:
                display_df['Assigned At'] = pd.to_datetime(display_df['Assigned At']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display the dataframe
            st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.markdown("### Add/Edit Device")
        
        # Get devices for dropdown
        if st.session_state.devices:
            df = pd.DataFrame(st.session_state.devices)
            
            # Filter out entries with null or empty device_id
            valid_devices = df[df['device_id'].notna() & (df['device_id'] != '')]
            
            if not valid_devices.empty:
                # Add a separator between edit existing and create new
                st.markdown("#### Select a Device to Edit")
                
                # Select a device to edit or delete
                selected_device_id = st.selectbox(
                    "Choose a device",
                    options=["-- Create New Device --"] + valid_devices['device_id'].tolist(),
                    format_func=lambda x: x if x == "-- Create New Device --" else f"{x} - {valid_devices[valid_devices['device_id'] == x]['device_name'].values[0] if not valid_devices[valid_devices['device_id'] == x]['device_name'].isna().values[0] else 'Unnamed'}"
                )
                
                col1, col2 = st.columns(2)
                
                if selected_device_id != "-- Create New Device --":
                    with col1:
                        if st.button("✏️ Load for Editing", key="load_selected_device"):
                            # Find the device in the list and set it as the current edit device
                            st.session_state.edit_device = next(
                                (device for device in st.session_state.devices if device['device_id'] == selected_device_id),
                                None
                            )
                            st.success(f"Device '{selected_device_id}' loaded for editing.")
                    
                    with col2:
                        if st.button("🗑️ Delete Device", key="delete_selected_device"):
                            if delete_device(selected_device_id):
                                # Update session state to reflect the change
                                st.session_state.devices = [device for device in st.session_state.devices if device['device_id'] != selected_device_id]
                                if st.session_state.edit_device and st.session_state.edit_device.get('device_id') == selected_device_id:
                                    st.session_state.edit_device = None
                                
                                st.success(f"Device {selected_device_id} deleted successfully!")
                            else:
                                st.error(f"Failed to delete device {selected_device_id}.")
                
                st.divider()
        
        # Check if we're editing an existing device
        is_editing = st.session_state.edit_device is not None
        device_to_edit = st.session_state.edit_device or {}
        
        # Show notification if we're editing a device
        if is_editing:
            st.markdown("#### Edit Device")
            st.info(f"Editing device: {device_to_edit.get('device_id', '')}")
        else:
            st.markdown("#### Create New Device")
        
        # Device ID field - readonly if editing
        device_id = st.text_input(
            "Device ID",
            value=device_to_edit.get('device_id', ''),
            disabled=is_editing,
            placeholder="e.g., NFC_ABC123"
        )
        
        # Device name field
        device_name = st.text_input(
            "Device Name",
            value=device_to_edit.get('device_name', ''),
            placeholder="e.g., Main Office Reader, Home NFC Reader"
        )
        
        # Location field
        location = st.text_input(
            "Location",
            value=device_to_edit.get('location', ''),
            placeholder="e.g., Office Desk, Front Door"
        )
        
        # Notes field
        notes = st.text_area(
            "Notes",
            value=device_to_edit.get('notes', ''),
            placeholder="Additional information about this device..."
        )
        
        # Submit button
        if st.button("💾 Save Device", key="save_device"):
            if not is_editing and not device_id:
                st.error("Device ID is required!")
            else:
                # Prepare data for save
                device_data = {
                    'device_name': device_name,
                    'location': location,
                    'notes': notes
                }
                
                # Add device_id only for new devices
                if not is_editing:
                    device_data['device_id'] = device_id
                
                # Save to Supabase
                if create_update_device(device_data, device_id if is_editing else None):
                    # Refresh device list
                    st.session_state.devices = fetch_all_devices()
                    
                    # Reset edit state
                    st.session_state.edit_device = None
                    
                    # Show success message
                    st.success(f"Device {device_id} {'updated' if is_editing else 'created'} successfully!")
                    st.balloons()
                else:
                    st.error(f"Failed to {'update' if is_editing else 'create'} device.")
        
        # Cancel button (only show when editing)
        if is_editing and st.button("❌ Cancel", key="cancel_edit"):
            st.session_state.edit_device = None
            st.info("Edit canceled.")