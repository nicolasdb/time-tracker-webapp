"""
Tag management component for the time tracker application.
"""
import logging
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional

from utils.supabase import get_supabase_client, authenticate_service_role

logger = logging.getLogger(__name__)

def fetch_all_tags() -> List[Dict[str, Any]]:
    """
    Fetch all tag assignments from Supabase.
    
    Returns:
        List of tag assignment dictionaries or empty list if no data
    """
    client = get_supabase_client()
    
    # First try with regular client
    if client:
        try:
            response = client.table('tag_assignments').select('*').order('assigned_at', desc=True).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} tags with regular client")
                return response.data
        except Exception as e:
            logger.warning(f"Failed to fetch tags with regular client: {str(e)}")
    
    # Try with service role if regular client failed
    service_client = authenticate_service_role()
    if service_client:
        try:
            response = service_client.table('tag_assignments').select('*').order('assigned_at', desc=True).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} tags with service role client")
                return response.data
        except Exception as e:
            logger.warning(f"Failed to fetch tags with service role client: {str(e)}")
    
    # Return empty list if all attempts failed
    return []

def create_update_tag(tag_data: Dict[str, Any], tag_id: Optional[str] = None) -> bool:
    """
    Create or update a tag assignment in Supabase.
    
    Args:
        tag_data: Dictionary with tag data fields
        tag_id: Optional tag_id for update operations
    
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
        if tag_id:
            # Update existing tag
            response = supabase.table('tag_assignments').update(tag_data).eq('tag_id', tag_id).execute()
            if response.data:
                logger.info(f"Updated tag: {tag_id}")
                return True
        else:
            # Create new tag
            response = supabase.table('tag_assignments').insert(tag_data).execute()
            if response.data:
                logger.info(f"Created new tag: {tag_data['tag_id']}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to {'update' if tag_id else 'create'} tag: {str(e)}")
        return False

def delete_tag(tag_id: str) -> bool:
    """
    Delete a tag assignment from Supabase.
    
    Args:
        tag_id: ID of the tag to delete
    
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
        response = supabase.table('tag_assignments').delete().eq('tag_id', tag_id).execute()
        if response:
            logger.info(f"Deleted tag: {tag_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to delete tag: {str(e)}")
        return False

def display_tag_management():
    """
    Display the tag management interface with CRUD operations.
    """
    # Header removed to avoid duplication with page title
    
    # Initialize state variables if they don't exist
    if 'tags' not in st.session_state:
        st.session_state.tags = fetch_all_tags()
    
    if 'edit_tag' not in st.session_state:
        st.session_state.edit_tag = None
    
    if 'tag_filter' not in st.session_state:
        st.session_state.tag_filter = ""
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Tag List", "Add/Edit Tag"])
    
    with tab1:
        # Add refresh button and search/filter
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Refresh", key="refresh_tags"):
                st.session_state.tags = fetch_all_tags()
                st.success("Tag list refreshed!")
        
        with col2:
            st.session_state.tag_filter = st.text_input(
                "🔍 Search tags",
                value=st.session_state.tag_filter,
                placeholder="Filter by tag ID or project name..."
            )
        
        # Display tag list
        if not st.session_state.tags:
            st.info("No tags found. Add a new tag using the 'Add/Edit Tag' tab.")
        else:
            # Convert to dataframe for display
            df = pd.DataFrame(st.session_state.tags)
            
            # Apply filter if specified
            if st.session_state.tag_filter:
                filter_term = st.session_state.tag_filter.lower()
                filter_mask = df['tag_id'].astype(str).str.lower().str.contains(filter_term)
                
                if 'project_name' in df.columns:
                    project_mask = df['project_name'].fillna('').astype(str).str.lower().str.contains(filter_term)
                    filter_mask = filter_mask | project_mask
                
                df = df[filter_mask]
            
            # Format the dataframe for display
            display_df = df.copy()
            
            # Rename columns for better display
            column_renames = {
                'tag_id': 'Tag ID',
                'project_name': 'Project',
                'task_name': 'Task',
                'is_reflection_trigger': 'Reflection Trigger',
                'assigned_at': 'Assigned At'
            }
            display_df = display_df.rename(columns={k: v for k, v in column_renames.items() if k in display_df.columns})
            
            # Format date columns for better readability
            if 'Assigned At' in display_df.columns:
                display_df['Assigned At'] = pd.to_datetime(display_df['Assigned At']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display the dataframe
            st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.markdown("### Add/Edit Tag")
        
        # Get tags for dropdown
        if st.session_state.tags:
            df = pd.DataFrame(st.session_state.tags)
            
            # Add a separator between edit existing and create new
            st.markdown("#### Select a Tag to Edit")
            
            # Select a tag to edit or delete
            selected_tag_id = st.selectbox(
                "Choose a tag",
                options=["-- Create New Tag --"] + df['tag_id'].tolist(),
                format_func=lambda x: x if x == "-- Create New Tag --" else f"{x} - {df[df['tag_id'] == x]['project_name'].values[0] if df[df['tag_id'] == x]['project_name'].values[0] else 'Unassigned'}"
            )
            
            col1, col2 = st.columns(2)
            
            if selected_tag_id != "-- Create New Tag --":
                with col1:
                    if st.button("✏️ Load for Editing", key="load_selected_tag"):
                        # Find the tag in the list and set it as the current edit tag
                        st.session_state.edit_tag = next(
                            (tag for tag in st.session_state.tags if tag['tag_id'] == selected_tag_id),
                            None
                        )
                        st.success(f"Tag '{selected_tag_id}' loaded for editing.")
                
                with col2:
                    if st.button("🗑️ Delete Tag", key="delete_selected_tag"):
                        if delete_tag(selected_tag_id):
                            # Update session state to reflect the change
                            st.session_state.tags = [tag for tag in st.session_state.tags if tag['tag_id'] != selected_tag_id]
                            if st.session_state.edit_tag and st.session_state.edit_tag.get('tag_id') == selected_tag_id:
                                st.session_state.edit_tag = None
                            
                            st.success(f"Tag {selected_tag_id} deleted successfully!")
                        else:
                            st.error(f"Failed to delete tag {selected_tag_id}.")
            
            st.divider()
            
        # Check if we're editing an existing tag
        is_editing = st.session_state.edit_tag is not None
        tag_to_edit = st.session_state.edit_tag or {}
        
        # Show notification if we're editing a tag
        if is_editing:
            st.markdown("#### Edit Tag")
            st.info(f"Editing tag: {tag_to_edit.get('tag_id', '')}")
        else:
            st.markdown("#### Create New Tag")
        
        # Tag ID field - readonly if editing
        tag_id = st.text_input(
            "Tag ID",
            value=tag_to_edit.get('tag_id', ''),
            disabled=is_editing,
            placeholder="e.g., dd 54 2a 83"
        )
        
        # Project name field
        project_name = st.text_input(
            "Project Name",
            value=tag_to_edit.get('project_name', ''),
            placeholder="e.g., Work, Personal, Learning"
        )
        
        # Task name field
        task_name = st.text_input(
            "Task Name",
            value=tag_to_edit.get('task_name', ''),
            placeholder="e.g., Email, Programming, Research"
        )
        
        # Reflection trigger checkbox
        is_reflection_trigger = st.checkbox(
            "Trigger Reflection",
            value=tag_to_edit.get('is_reflection_trigger', False),
            help="When checked, this tag will trigger a reflection when it's used."
        )
        
        # Submit button
        if st.button("💾 Save Tag", key="save_tag"):
            if not is_editing and not tag_id:
                st.error("Tag ID is required!")
            else:
                # Prepare data for save
                tag_data = {
                    'project_name': project_name,
                    'task_name': task_name,
                    'is_reflection_trigger': is_reflection_trigger,
                }
                
                # Add tag_id only for new tags
                if not is_editing:
                    tag_data['tag_id'] = tag_id
                
                # Save to Supabase
                if create_update_tag(tag_data, tag_id if is_editing else None):
                    # Refresh tag list
                    st.session_state.tags = fetch_all_tags()
                    
                    # Reset edit state
                    st.session_state.edit_tag = None
                    
                    # Use a placeholder above the form to show the success message
                    st.success(f"Tag {tag_id} {'updated' if is_editing else 'created'} successfully!")
                    # Refresh the page after a short delay to show the changes
                    st.balloons()
                else:
                    st.error(f"Failed to {'update' if is_editing else 'create'} tag.")
        
        # Cancel button (only show when editing)
        if is_editing and st.button("❌ Cancel", key="cancel_edit"):
            st.session_state.edit_tag = None
            st.info("Edit canceled.")