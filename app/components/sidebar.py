"""
Sidebar component for the time tracker application.
"""
import logging
import streamlit as st

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
        
        # Get navigation options
        nav_options = ["Dashboard", "Track Time", "Tag Management", "Device Management", "Projects", "Reports"]
        
        # Initialize navigation state if not present
        if "navigation" not in st.session_state:
            st.session_state.navigation = "Dashboard"
        
        # Find the index of the current selection
        try:
            current_idx = nav_options.index(st.session_state.navigation)
        except ValueError:
            current_idx = 0
        
        # Add navigation with key for callback handling
        selected = st.radio(
            "Navigation",
            nav_options,
            index=current_idx,
            key="navigation"
        )
        
        st.divider()
        
        # About section
        st.markdown("---")
        st.markdown("v0.2.0 | Time Tracker")
        
    # No need to return anything since we're using session state for navigation