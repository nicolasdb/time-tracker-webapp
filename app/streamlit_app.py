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
        # Display sidebar and get selected page
        display_sidebar()
        selected_page = st.session_state.navigation
        
        # Initialize environment
        init_environment()
        
        # Main content area
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
            
            # Display navigation cards
            st.write("### Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("##### Manage Tags")
                st.markdown("Add or edit tags to categorize your activities")
                if st.button("Open Tag Management", key="goto_tags"):
                    # Set session state and rerun to navigate
                    st.session_state.navigation = "Tag Management"
                    st.rerun()
            
            with col2:
                st.info("##### Manage Devices")
                st.markdown("Configure your NFC readers and locations")
                if st.button("Open Device Management", key="goto_devices"):
                    # Set session state and rerun to navigate
                    st.session_state.navigation = "Device Management"
                    st.rerun()
            
            with col3:
                st.info("##### View Reports")
                st.markdown("Analyze your time data with visual reports")
                if st.button("Open Reports", key="goto_reports"):
                    # Set session state and rerun to navigate
                    st.session_state.navigation = "Reports"
                    st.rerun()
            
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