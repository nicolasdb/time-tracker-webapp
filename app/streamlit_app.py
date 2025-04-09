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
from components.results import display_test_results

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
        selected_page = display_sidebar()
        
        # Initialize environment
        init_environment()
        
        # Main content area
        if selected_page == "Dashboard":
            # Main title with description
            st.title("⏱️ Time Tracker Dashboard")
            st.markdown("""
                Track your time on different projects and tasks to improve productivity.
            """)
            
            # Display test results for Stage 1 validation
            display_test_results()
            
        elif selected_page == "Track Time":
            st.title("🕒 Track Time")
            st.info("Time tracking functionality will be implemented in a future stage.")
            
        elif selected_page == "Projects":
            st.title("📁 Projects")
            st.info("Project management functionality will be implemented in a future stage.")
            
        elif selected_page == "Reports":
            st.title("📊 Reports")
            st.info("Reporting functionality will be implemented in a future stage.")
            
        # Display configuration questions at the bottom
        display_configuration_questions()
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("⚠️ An error occurred while loading the application")
        st.error(f"Error details: {str(e)}")
        st.error("Please check the application logs for more information.")

if __name__ == "__main__":
    main()