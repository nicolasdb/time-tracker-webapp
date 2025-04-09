"""
Sidebar component for the time tracker application.
"""
import logging
import streamlit as st

# Configure logging
logger = logging.getLogger(__name__)

def display_sidebar():
    """
    Display sidebar with navigation and options.
    """
    with st.sidebar:
        st.title("⏱️ Time Tracker")
        
        # Add navigation
        selected = st.radio(
            "Navigation",
            ["Dashboard", "Track Time", "Projects", "Reports"],
            index=0
        )
        
        st.divider()
        
        # Settings section
        with st.expander("Settings"):
            st.checkbox("Dark mode")
            st.selectbox("Time format", ["12-hour", "24-hour"])
        
        # About section
        st.markdown("---")
        st.markdown("v0.1.0 | [Documentation](https://github.com/yourrepo)")
        
    return selected