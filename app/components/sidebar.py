"""
Sidebar component for the time tracker application.
"""
import os
import logging
import streamlit as st
from utils.auth import get_current_user, get_current_user_email, sign_out

# Configure logging
logger = logging.getLogger(__name__)

def set_nav_callback():
    """Callback when sidebar navigation changes"""
    # This will be triggered automatically when the radio button value changes
    # because we're using the key="navigation" parameter
    # No action needed here - st.session_state.navigation is already updated

def display_sidebar():
    """
    Display sidebar with navigation and options.
    """
    with st.sidebar:
        st.title("⏱️ Time Tracker")
        
        # Check authentication state from session state directly
        is_authenticated = st.session_state.auth.get("authenticated", False)
        
        if is_authenticated:
            # User info section
            user_email = get_current_user_email() or 'User'
            st.markdown(f"👤 **{user_email}**")
            
            # Add debug information in case we have issues
            if os.getenv("DEBUG_MODE") == "True":
                st.caption(f"Auth token (first 8 chars): {st.session_state.auth.get('access_token', '')[:8]}...")
                if "_auth" in st.query_params:
                    st.caption(f"URL token: {st.query_params['_auth'][:8]}...")
            
            # Get navigation options
            nav_options = ["Dashboard", "Track Time", "Tag Management", "Device Management", "Projects", "Reports"]
            
            # Initialize navigation state if not present
            if "navigation" not in st.session_state:
                st.session_state.navigation = "Dashboard"
            
            # Add navigation with key for callback handling
            selected = st.radio(
                "Choose an option:",
                nav_options,
                index=nav_options.index(st.session_state.navigation),
                key="navigation"
            )
            
            # Update navigation state only if it has changed
            if selected != st.session_state.navigation:
                st.session_state.navigation = selected
                st.experimental_rerun()
            
            st.divider()
            
            # Sign out button
            if st.button("Sign Out"):
                success, error = sign_out()
                if success:
                    st.session_state["signed_out"] = True
                    st.rerun()
                else:
                    st.error(f"Failed to sign out: {error}")
        else:
            # If not authenticated, just show login options in the sidebar
            st.warning("You must log in to access the application")
            if "navigation" not in st.session_state or st.session_state.navigation != "Login":
                st.session_state.navigation = "Login"
        
        # About section
        st.markdown("---")
        st.markdown("v0.3.0 | Time Tracker")
        
    # No need to return anything since we're using session state for navigation