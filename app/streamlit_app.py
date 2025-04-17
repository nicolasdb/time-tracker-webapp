"""
Main Streamlit application for the time tracker webapp.
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv

# Import components
from components.sidebar import display_sidebar
from components.questions import display_configuration_questions
from components.tag_management import display_tag_management
from components.device_management import display_device_management
from components.time_tracking import display_time_tracking

# Import utils
from utils.data_loader import test_connection
from utils.auth import initialize_auth, display_login_form, ensure_authenticated

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_environment():
    """Initialize environment variables and connections."""
    # Load environment variables
    load_dotenv()
    
    # Check Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.warning("⚠️ Supabase configuration not found. Some features may be limited.")
        logger.warning("Supabase environment variables not set")
        return False
    
    # Test connection
    connection_ok = test_connection()
    st.session_state["connection_ok"] = connection_ok
    
    if not connection_ok:
        st.warning("⚠️ Could not connect to Supabase. Please check your configuration.")
        logger.warning("Failed to connect to Supabase")
    
    return connection_ok

def main():
    """Main function to run the Streamlit application."""
    # Page config
    st.set_page_config(
        page_title="Time Tracker",
        page_icon="⏱️",
        layout="wide",
    )
    
    try:
        # Check for redirect flags
        if st.session_state.get("signed_out", False):
            # Clear the flag
            del st.session_state["signed_out"]
            # Set navigation to Login before rendering the sidebar
            if "navigation" in st.session_state:
                st.session_state.navigation = "Login"
            logger.info("User signed out, redirecting to Login page")
        
        # Just handle the signed_out flag, no more redirect flags
        # This simplifies the logic and prevents redirect loops
        
        # Clear any stale redirect flags that might be in the session state
        # to completely break any existing loops
        if "redirect_to_login" in st.session_state:
            del st.session_state["redirect_to_login"]
        if "auth_redirect_to_login" in st.session_state:
            del st.session_state["auth_redirect_to_login"]
        if "redirect_count" in st.session_state:
            del st.session_state["redirect_count"]
        
        # Initialize environment and authentication
        init_environment()
        
        # Log authentication state before initialization
        logger.debug(f"Before initialize_auth(): Auth state exists: {'auth' in st.session_state}")
        if 'auth' in st.session_state:
            logger.debug(f"Before initialize_auth(): Authenticated: {st.session_state.auth.get('authenticated', False)}")
        
        # Initialize authentication
        initialize_auth()
        
        # Log authentication state after initialization
        logger.debug(f"After initialize_auth(): Authenticated: {st.session_state.auth.get('authenticated', False)}")
        if st.session_state.auth.get('authenticated', False):
            logger.debug(f"After initialize_auth(): User: {st.session_state.auth.get('user')}")
        
        # Display sidebar and get selected page
        display_sidebar()
        selected_page = st.session_state.get("navigation", "Dashboard") # Changed to get the value from session state
        
        # Log current navigation
        logger.debug(f"Current navigation: {selected_page}")
        
        # Handle login page separately
        if selected_page == "Login":
            logger.debug("Showing login form")
            display_login_form()
            return
        
        # Main content area - require authentication for all other pages
        logger.debug("Checking authentication for protected page")
        if not ensure_authenticated():
            logger.debug("Authentication check failed, handling in ensure_authenticated")
            # Important: do NOT rerun here - just show the login page
            display_login_form()
            return
            
        if selected_page == "Dashboard":
            # Main title with description
            st.title("⏱️ Time Tracker Dashboard")
            st.markdown("""
                Track your time on different projects and tasks to improve productivity.
            """)
            
            # Create a clean dashboard layout
            st.write("### Recent Activity")
            
            # Get today's date
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get real metrics from time tracking data
            from components.time_tracking import get_dashboard_metrics, format_duration
            
            metrics = get_dashboard_metrics()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Active Projects", str(metrics['active_projects']))
                st.metric("Total Tags", str(metrics['total_tags']))
                st.metric("Devices", str(metrics['total_devices']))
            
            with col2:
                st.metric("Today's Activity", format_duration(metrics['today_time']))
                st.metric("Week Total", format_duration(metrics['week_time']))
                st.metric("Tasks Completed", str(metrics['completed_tasks']))
            
            # Removed the Quick Actions section
            # Removed the columns for quick actions
            # Removed buttons for Tag Management, Device Management, and Reports
                    
       
        elif selected_page == "Track Time":
            st.title("🕒 Track Time")
            st.markdown("""
                View your time tracking data from RFID events and see how your time is spent.
            """)
            
            # Display the time tracking component
            display_time_tracking()
        
        elif selected_page == "Tag Management":
            st.title("🏷️ Tag Management")
            st.markdown("""
                Manage your RFID tags, assign them to projects and tasks, and set reflection triggers.
            """)
            display_tag_management()
            
        elif selected_page == "Device Management":
            st.title("📱 Device Management")
            st.markdown("""
                Manage your NFC reader devices, assign names and locations, and add notes.
            """)
            display_device_management()
            
        elif selected_page == "Projects":
            st.title("📁 Projects")
            st.info("Project management functionality will be implemented in a future stage.")
            
        elif selected_page == "Reports":
            st.title("📊 Reports")
            st.info("Reporting functionality will be implemented in a future stage.")
            
        # Optional debugging information
        if os.getenv("DEBUG_MODE") == "True":
            st.divider()
            st.caption("Debug Mode Enabled")
            display_configuration_questions()
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("⚠️ An error occurred while loading the application")
        st.error(f"Error details: {str(e)}")
        st.error("Please check the application logs for more information.")

if __name__ == "__main__":
    main()