"""
Main Streamlit application for the time tracker webapp.
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv

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

def main():
    """Main function to run the Streamlit application."""
    # Initialize environment
    init_environment()
    
    # Page config
    st.set_page_config(
        page_title="Time Tracker",
        page_icon="⏱️",
        layout="wide",
    )
    
    try:
        # Main title with description
        st.title("⏱️ Time Tracker")
        st.markdown("""
            Track your time on different projects and tasks to improve productivity.
        """)
        
        # Placeholder for app content
        st.info("This application is under development.")
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("⚠️ An error occurred while loading the application")
        st.error(f"Error details: {str(e)}")
        st.error("Please check the application logs for more information.")

if __name__ == "__main__":
    main()