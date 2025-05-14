"""
Authentication utilities for the Time Tracker application.
"""
import os
import logging
import json
import streamlit as st
import re
import pickle
import base64
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from pathlib import Path

from utils.supabase import get_supabase_client

# Configure logging
logger = logging.getLogger(__name__)

# Path to store auth data
AUTH_DATA_PATH = Path("/tmp/.auth_session")

def save_auth_session(auth_data):
    """
    Save authentication session data to file.
    
    Args:
        auth_data: The auth session data to save
    """
    try:
        # Create a serializable version of the auth data (exclude non-serializable objects)
        serializable_data = {
            "authenticated": auth_data.get("authenticated", False),
            "access_token": auth_data.get("access_token"),
            "refresh_token": auth_data.get("refresh_token"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Only save user and session if they exist and are serializable
        if auth_data.get("user"):
            user = auth_data["user"]
            try:
                # Extract key user information
                serializable_data["user_id"] = getattr(user, "id", None)
                serializable_data["user_email"] = getattr(user, "email", None)
            except Exception as user_error:
                logger.warning(f"Could not serialize user data: {str(user_error)}")
        
        # Make sure data directory exists
        os.makedirs(os.path.dirname(AUTH_DATA_PATH), exist_ok=True)
        
        # Encode and save the data
        with open(AUTH_DATA_PATH, "wb") as f:
            pickled_data = pickle.dumps(serializable_data)
            encoded_data = base64.b64encode(pickled_data)
            f.write(encoded_data)
            
        logger.debug(f"Auth session saved to {AUTH_DATA_PATH}")
    except Exception as e:
        logger.error(f"Error saving auth session: {str(e)}")

def load_auth_session():
    """
    Load authentication session data from file.
    
    Returns:
        Dict with auth data or None if not found or expired
    """
    try:
        if not os.path.exists(AUTH_DATA_PATH):
            logger.debug("No saved auth session found")
            return None
            
        # Load and decode the data
        with open(AUTH_DATA_PATH, "rb") as f:
            encoded_data = f.read()
            pickled_data = base64.b64decode(encoded_data)
            auth_data = pickle.loads(pickled_data)
        
        # Check if session is expired (24 hours)
        if "timestamp" in auth_data:
            saved_time = datetime.fromisoformat(auth_data["timestamp"])
            if datetime.now() - saved_time > timedelta(hours=24):
                logger.debug("Saved auth session is expired")
                return None
        
        logger.debug(f"Loaded auth session from {AUTH_DATA_PATH}")
        return auth_data
    except Exception as e:
        logger.error(f"Error loading auth session: {str(e)}")
        return None

def initialize_auth():
    """
    Initialize the authentication state in the session.
    """
    # Initialize auth session state if not present
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "authenticated": False,
            "user": None,
            "access_token": None,
            "refresh_token": None,
            "session": None
        }
    
    # Initialize other auth-related session states
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "signin"  # signin, magic_link, reset_password
    
    if "magic_link_sent" not in st.session_state:
        st.session_state.magic_link_sent = False
    
    if "reset_password_sent" not in st.session_state:
        st.session_state.reset_password_sent = False
    
    # Add limited JavaScript for cookie management - just to save cookies, not to trigger refreshes
    st.markdown("""
    <script>
    // Function to get cookie by name
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    // Function to set cookie
    function setCookie(name, value, days) {
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
    }
    
    // DO NOT add cookie to URL params automatically - this was causing infinite loops
    </script>
    """, unsafe_allow_html=True)
    
    # Check URL parameters for access_token and refresh_token (for magic link flows)
    try:
        if "access_token" in st.query_params and "refresh_token" in st.query_params:
            access_token = st.query_params["access_token"]
            refresh_token = st.query_params["refresh_token"]
            
            # Call set_session with tokens
            success = set_session_from_tokens(access_token, refresh_token)
            
            if success:
                # Save the auth session
                save_auth_session(st.session_state.auth)
                
                # Clear query parameters and redirect to dashboard
                st.query_params.clear()
                st.session_state.navigation = "Dashboard"
                st.rerun()
    except Exception as e:
        logger.error(f"Error handling URL parameters: {str(e)}")
    
    # Only attempt to reconnect if we're not already authenticated
    if not st.session_state.auth["authenticated"]:
        # Try these approaches in order:
        
        # 1. Use refresh token if available in session state
        if st.session_state.auth["refresh_token"]:
            logger.info("Attempting to refresh session with stored refresh token")
            success = try_refresh_session()
            if success:
                logger.info("Session refreshed successfully from session state token")
                save_auth_session(st.session_state.auth)
                return
        
        # 2. Try to load saved session from file
        saved_session = load_auth_session()
        if (saved_session and saved_session.get("refresh_token")):
            logger.info("Found saved auth session, attempting to use it")
            # Set tokens from saved session
            st.session_state.auth["refresh_token"] = saved_session["refresh_token"]
            if saved_session.get("access_token"):
                st.session_state.auth["access_token"] = saved_session["access_token"]
            
            # Try to refresh with these tokens
            success = try_refresh_session()
            if success:
                logger.info("Session refreshed successfully from saved file")
                return
        
        # 3. Try to use the Supabase persistent session
        try:
            client = get_supabase_client()
            if client:
                # Try to get current session
                try:
                    logger.info("Attempting to get current Supabase session")
                    session = client.auth.get_session()
                    
                    if session:
                        user = client.auth.get_user()
                        
                        if user and user.user:
                            # Update auth state
                            st.session_state.auth = {
                                "authenticated": True,
                                "user": user.user,
                                "access_token": session.access_token, 
                                "refresh_token": session.refresh_token,
                                "session": session
                            }
                            logger.info(f"Session restored for user: {user.user.email}")
                            save_auth_session(st.session_state.auth)
                            return
                except Exception as session_error:
                    logger.error(f"Error getting Supabase session: {str(session_error)}")
        except Exception as e:
            logger.error(f"Error initializing auth: {str(e)}")

def set_session_from_tokens(access_token: str, refresh_token: str) -> bool:
    """
    Set the session state from access and refresh tokens.
    
    Args:
        access_token: JWT access token
        refresh_token: JWT refresh token
        
    Returns:
        Boolean indicating success
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False
        
        # Set session manually
        client.auth.set_session(access_token, refresh_token)
        
        # Get user from session
        user = client.auth.get_user()
        session = client.auth.get_session()
        
        if user and session:
            # Store auth state
            st.session_state.auth = {
                "authenticated": True,
                "user": user.user,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "session": session
            }
            
            logger.info(f"Session set from tokens successfully for user: {user.user.email}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error setting session from tokens: {str(e)}")
        return False

def sign_in(email: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Sign in a user with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False, "Database connection error"
        
        # Attempt to sign in
        try:
            # Explicitly try to set persist_session to true 
            # This only works in browser context, not server-side
            response = client.auth.sign_in_with_password({
                "email": email, 
                "password": password,
                "options": {
                    "persistent_session": True
                }
            })
            
            if not response or not response.user or not response.session:
                logger.error("Sign in response missing user or session")
                return False, "Authentication failed. Please try again."
            
            # Store auth state in session state
            st.session_state.auth = {
                "authenticated": True,
                "user": response.user,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "session": response.session
            }
            
            # Save the auth session to file for persistence
            save_auth_session(st.session_state.auth)
            
            # Add auth token to URL params immediately for cookie saving
            token = response.session.access_token[:30]
            # st.query_params["_auth"] = token  # <-- This line is already commented out, keep it removed!
            
            # Add custom JavaScript to set cookie immediately
            st.markdown(f"""
            <script>
                function setCookie(name, value, days) {{
                    let expires = "";
                    if (days) {{
                        const date = new Date();
                        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                        expires = "; expires=" + date.toUTCString();
                    }}
                    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
                }}
                
                // Set auth cookie for 7 days
                setCookie('_auth_token', '{token}', 7);
                console.log('Auth cookie set successfully');
            </script>
            """, unsafe_allow_html=True)
            
            # Log success
            logger.info(f"User signed in: {email}")
            logger.debug(f"Session tokens stored: access={response.session.access_token[:10]}..., refresh={response.session.refresh_token[:10]}...")
            
            return True, None
        except Exception as auth_error:
            logger.error(f"Supabase auth error: {str(auth_error)}")
            return False, format_auth_error(str(auth_error))
        
    except Exception as e:
        logger.error(f"Sign in error: {str(e)}")
        return False, format_auth_error(str(e))

def send_magic_link(email: str) -> Tuple[bool, Optional[str]]:
    """
    Send a magic link to the user's email.
    
    Args:
        email: User email
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False, "Database connection error"
        
        # Validate email format
        if not is_valid_email(email):
            return False, "Please enter a valid email address"
        
        # Construct the redirect URL (current URL)
        redirect_to = None  # Uses the Site URL configured in Supabase
        
        # Send magic link
        client.auth.sign_in_with_otp({
            "email": email,
            "options": {
                "email_redirect_to": redirect_to
            }
        })
        
        logger.info(f"Magic link sent to: {email}")
        return True, None
        
    except Exception as e:
        logger.error(f"Magic link error: {str(e)}")
        return False, format_auth_error(str(e))

def send_password_reset(email: str) -> Tuple[bool, Optional[str]]:
    """
    Send a password reset link to the user's email.
    
    Args:
        email: User email
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False, "Database connection error"
        
        # Validate email format
        if not is_valid_email(email):
            return False, "Please enter a valid email address"
        
        # Send password reset email
        client.auth.reset_password_for_email(email)
        
        logger.info(f"Password reset email sent to: {email}")
        return True, None
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return False, format_auth_error(str(e))

def sign_out() -> Tuple[bool, Optional[str]]:
    """
    Sign out the current user.
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False, "Database connection error"
        
        # Attempt to sign out
        client.auth.sign_out()
        
        # Reset auth state
        st.session_state.auth = {
            "authenticated": False,
            "user": None,
            "access_token": None,
            "refresh_token": None,
            "session": None
        }
        
        # Delete the saved session file if it exists
        try:
            if os.path.exists(AUTH_DATA_PATH):
                os.remove(AUTH_DATA_PATH)
                logger.debug(f"Deleted auth session file: {AUTH_DATA_PATH}")
        except Exception as del_error:
            logger.warning(f"Failed to delete auth session file: {str(del_error)}")
        
        # Add JavaScript to remove the cookie
        st.markdown("""
        <script>
            // Delete cookie by setting expiration in the past
            document.cookie = "_auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax";
            console.log('Auth cookie cleared');
        </script>
        """, unsafe_allow_html=True)
        
        logger.info("User signed out")
        return True, None
        
    except Exception as e:
        logger.error(f"Sign out error: {str(e)}")
        return False, format_auth_error(str(e))

def try_refresh_session() -> bool:
    """
    Try to refresh the auth session using the refresh token.
    
    Returns:
        Boolean indicating success
    """
    if not st.session_state.auth["refresh_token"]:
        logger.warning("No refresh token available, cannot refresh session")
        return False
        
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False
        
        refresh_token = st.session_state.auth["refresh_token"]
        logger.debug(f"Attempting to refresh with token: {refresh_token[:10]}...")
        
        # Try multiple strategies for session refresh
        
        # Strategy 1: Set session explicitly and then refresh
        try:
            # First try to set the current session with the tokens we have
            if st.session_state.auth["access_token"]:
                logger.debug("Setting session with stored tokens")
                client.auth.set_session(
                    st.session_state.auth["access_token"],
                    refresh_token
                )
                
                # Then try to refresh the session
                logger.debug("Refreshing session")
                response = client.auth.refresh_session()
                
                if response and response.session:
                    # Update auth state
                    st.session_state.auth = {
                        "authenticated": True,
                        "user": response.user,
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "session": response.session
                    }
                    
                    logger.info("Session refreshed successfully using strategy 1")
                    logger.debug(f"New tokens: access={response.session.access_token[:10]}..., refresh={response.session.refresh_token[:10]}...")
                    return True
        except Exception as refresh_error:
            logger.warning(f"Strategy 1 failed: {str(refresh_error)}")
            
        # Strategy 2: Get the current session
        try:
            logger.debug("Getting current session")
            session = client.auth.get_session()
            
            if session:
                user = client.auth.get_user()
                
                if user and user.user:
                    # Update auth state from current session
                    st.session_state.auth = {
                        "authenticated": True,
                        "user": user.user,
                        "access_token": session.access_token,
                        "refresh_token": session.refresh_token,
                        "session": session
                    }
                    logger.info("Session retrieved successfully using strategy 2")
                    logger.debug(f"Current tokens: access={session.access_token[:10]}..., refresh={session.refresh_token[:10]}...")
                    return True
        except Exception as get_error:
            logger.warning(f"Strategy 2 failed: {str(get_error)}")
                
        logger.error("All session refresh strategies failed")
        return False
        
    except Exception as e:
        logger.error(f"Session refresh error: {str(e)}")
        # Don't clear auth state here, as it might be temporary error
        return False

def get_current_user() -> Optional[Any]:
    """
    Get the current authenticated user.
    
    Returns:
        User object or None if not authenticated
    """
    if st.session_state.auth["authenticated"] and st.session_state.auth["user"]:
        return st.session_state.auth["user"]
    return None

def get_current_user_id() -> Optional[str]:
    """
    Get the current authenticated user's ID.
    
    Returns:
        User ID as string or None if not authenticated
    """
    user = get_current_user()
    if user and hasattr(user, 'id'):
        return user.id
    return None

def get_current_user_email() -> Optional[str]:
    """
    Get the current authenticated user's email.
    
    Returns:
        User email as string or None if not authenticated
    """
    user = get_current_user()
    if user and hasattr(user, 'email'):
        return user.email
    return None

def ensure_authenticated():
    """
    Ensure the user is authenticated. If not, redirect to login.

    Returns:
        Boolean indicating if user is authenticated
    """
    # 1. Check if we're already authenticated in session state
    if st.session_state.get("auth", {}).get("authenticated", False):
        return True

    # 2. Try to refresh session
    if st.session_state.get("auth", {}).get("refresh_token"):
        logger.info("Attempting to refresh session with stored refresh token")
        success = try_refresh_session()
        if success:
            logger.info("Session refreshed successfully from session state token")
            save_auth_session(st.session_state.auth)
            return True

    # 3. Try to load saved session from file
    saved_session = load_auth_session()
    if saved_session and saved_session.get("refresh_token"):
        logger.info("Found saved auth session, attempting to use it")
        # Set tokens from saved session
        st.session_state.auth = saved_session

        # Try to refresh with these tokens
        success = try_refresh_session()
        if success:
            logger.info("Session refreshed successfully from saved file")
            return True

    # 4. Last chance recovery: try getting session from Supabase
    logger.warning("User not authenticated, attempting final recovery")

    # Try to get session one more time before redirecting
    client = get_supabase_client()
    if client:
        try:
            logger.info("Getting current Supabase session")
            session = client.auth.get_session()

            if session:
                user = client.auth.get_user()

                if user and user.user:
                    # Update auth state
                    st.session_state.auth = {
                        "authenticated": True,
                        "user": user.user,
                        "access_token": session.access_token,
                        "refresh_token": session.refresh_token,
                        "session": session
                    }

                    # Save the session for future recovery
                    save_auth_session(st.session_state.auth)

                    logger.info(f"Last-minute authentication recovery for user: {user.user.email}")
                    return True
        except Exception as e:
            logger.error(f"Final authentication check failed: {str(e)}")

    # If we get here, authentication failed - redirect to login
    logger.info("Authentication check failed, redirecting to login")
    st.session_state.navigation = "Login"
    return False

def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        Boolean indicating if email is valid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
    
def sign_up(email: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Sign up a new user with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        if not client:
            logger.error("Failed to get Supabase client")
            return False, "Database connection error"
        
        # Validate email format
        if not is_valid_email(email):
            return False, "Please enter a valid email address"
        
        # Validate password strength
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Attempt to sign up
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            logger.info(f"User signed up: {email}")
            return True, None
        
        return False, "Failed to create account"
        
    except Exception as e:
        logger.error(f"Sign up error: {str(e)}")
        return False, format_auth_error(str(e))

def format_auth_error(error_message: str) -> str:
    """
    Format authentication error messages for user display.
    
    Args:
        error_message: The raw error message
        
    Returns:
        Formatted user-friendly error message
    """
    # Common error patterns and user-friendly messages
    if "invalid login credentials" in error_message.lower():
        return "Invalid email or password. Please try again."
    elif "rate limit exceeded" in error_message.lower():
        return "Too many login attempts. Please try again later."
    elif "user not found" in error_message.lower():
        return "User not found. Please check your email or sign up."
    elif "unable to validate email address" in error_message.lower():
        return "Invalid email format. Please check your email address."
    elif "network" in error_message.lower() or "connection" in error_message.lower():
        return "Network error. Please check your internet connection."
    else:
        return "Authentication error. Please try again or contact support."

def display_login_form():
    """
    Display the login form with multiple auth options.
    """
    st.title("🔐 Time Tracker Login")

    # Tab selection for different authentication methods
    tab1, tab2, tab3 = st.tabs(["Sign In", "Sign Up", "Reset Password"])

    with tab1:
        st.subheader("Sign in with Email and Password")
        
        with st.form("signin_form"):
            email = st.text_input("Email", key="signin_email")
            password = st.text_input("Password", type="password", key="signin_password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return False
                    
                with st.spinner("Signing in..."):
                    success, error = sign_in(email, password)
                    
                    if success:
                        st.success("Signed in successfully!")
                        st.session_state.navigation = "Dashboard"
                        # st.rerun()
                        # Inject JavaScript to reload the page
                        st.components.v1.html(
                            """
                            <script>
                                console.log("Reloading page...");
                                setTimeout(function() {
                                    window.parent.location.reload(); // Reload the parent window
                                }, 10);
                            </script>
                            """,
                            height=0,
                        )
                        return
                    else:
                        st.error(error)
                        return False
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password", 
                                     help="Password must be at least 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                    return False
                
                if password != confirm_password:
                    st.error("Passwords do not match")
                    return False
                
                with st.spinner("Creating account..."):
                    success, error = sign_up(email, password)
                    
                    if success:
                        st.success("Account created successfully! Please check your email for confirmation.")
                        return False
                    else:
                        st.error(error)
                        return False
        
        st.info("After signing up, you'll receive a confirmation email. Click the link in the email to verify your account before signing in.")
    
    with tab3:
        st.subheader("Reset Your Password")
        
        if st.session_state.reset_password_sent:
            st.success("Password reset email sent! Please check your email.")
            if st.button("I didn't receive the email", key="resend_reset_link"):
                st.session_state.reset_password_sent = False
                st.rerun()
        else:
            with st.form("reset_password_form"):
                email = st.text_input("Email", key="reset_password_email")
                submit = st.form_submit_button("Send Reset Link")
                
                if submit:
                    if not email:
                        st.error("Please enter your email")
                        return False
                        
                    with st.spinner("Sending password reset link..."):
                        success, error = send_password_reset(email)
                        
                        if success:
                            st.session_state.reset_password_sent = True
                            st.rerun()
                            return False
                        else:
                            st.error(error)
                            return False
    
    return False