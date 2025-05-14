"""
Questions component for collecting user input and preferences.
"""
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def display_configuration_questions():
    """
    Display configuration questions to the user.
    This is used for initial setup and customization.
    """
    st.header("⚙️ Configuration")
    
    with st.expander("Connection Settings", expanded=True):
        st.info("These settings are read from your environment variables.")
        
        # Display connection status
        if st.session_state.get("connection_ok", False):
            st.success("✅ Connected to Supabase")
        else:
            st.error("❌ Not connected to Supabase")
            
            # Show troubleshooting tips directly (not in a nested expander)
            st.markdown("**Troubleshooting Tips:**")
            st.markdown("""
            1. Check that your `.env` file contains valid Supabase credentials:
               - `SUPABASE_URL`
               - `SUPABASE_KEY`
            2. Restart the application after updating environment variables
            3. Verify that your Supabase project is active and accessible
            4. Make sure the database tables are created (see SETUP.md)
            """)
    
    with st.expander("Visualization Settings"):
        # Dummy controls for visualization preferences
        st.selectbox("Chart Type", ["Bar Chart", "Pie Chart", "Timeline"])
        st.slider("Display Limit", min_value=1, max_value=50, value=10)
        st.checkbox("Group by Category")
        
        # These don't actually do anything in Stage 1, just placeholders
        st.button("Save Preferences", disabled=True)