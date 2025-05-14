import os
from supabase import create_client, Client
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_PUBLISHABLE_KEY"))  # Support both key naming conventions

# For development, if the keys aren't set, create mock authentication functions
if not SUPABASE_URL or not SUPABASE_KEY or SUPABASE_URL == "https://example.supabase.co":
    logger.warning("Using mock Supabase authentication - only for development.")
    supabase = None
    
    def sign_up(email: str, password: str, name: str = None):
        """Mock sign-up function for development"""
        logger.info(f"MOCK: Signing up user with email {email}")
        # Return a mock user object
        return {
            "user": {
                "id": "mock-user-id",
                "email": email,
                "user_metadata": {"name": name}
            }
        }
    
    def sign_in(email: str, password: str):
        """Mock sign-in function for development"""
        logger.info(f"MOCK: Signing in user with email {email}")
        # Return a mock session
        return {
            "user": {
                "id": "mock-user-id",
                "email": email
            },
            "session": {
                "access_token": "mock-token",
                "expires_at": 9999999999
            }
        }
    
    def sign_out(token: str):
        """Mock sign-out function for development"""
        logger.info("MOCK: Signing out user")
        return {"success": True}

else:
    # Initialize real Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        def sign_up(email: str, password: str, name: str = None):
            """Register a new user with Supabase"""
            try:
                user = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                })
                
                # Log success
                logger.info(f"User registration successful for email: {email}")
                
                # If we have a name, update user metadata
                if name and user and hasattr(user, 'user') and user.user:
                    try:
                        # Store additional user data in a 'profiles' table if needed
                        # This is a common pattern with Supabase
                        result = supabase.table("profiles").insert({
                            "id": user.user.id,
                            "name": name,
                            "email": email
                        }).execute()
                        logger.info(f"User profile created: {result}")
                    except Exception as profile_error:
                        logger.error(f"Error creating user profile: {str(profile_error)}")
                        # Continue even if profile creation fails
                    
                return user
            except Exception as e:
                logger.error(f"Error during sign up: {e}")
                logger.error(f"Error type: {type(e)}")
                # Handle specific error cases
                if "User already registered" in str(e):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This email is already registered. Please login instead."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Registration failed: {str(e)}"
                    )

        def sign_in(email: str, password: str):
            """Sign in a user with Supabase"""
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                return response
            except Exception as e:
                logger.error(f"Error during sign in: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

        def sign_out(token: str):
            """Sign out a user"""
            try:
                supabase.auth.sign_out()
                return {"success": True}
            except Exception as e:
                logger.error(f"Error during sign out: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error signing out"
                )
    
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        logger.warning("Falling back to mock authentication")
        
        def sign_up(email: str, password: str, name: str = None):
            """Mock sign-up function as fallback"""
            logger.info(f"MOCK: Signing up user with email {email}")
            return {
                "user": {
                    "id": "mock-user-id",
                    "email": email,
                    "user_metadata": {"name": name}
                }
            }
        
        def sign_in(email: str, password: str):
            """Mock sign-in function as fallback"""
            logger.info(f"MOCK: Signing in user with email {email}")
            return {
                "user": {
                    "id": "mock-user-id",
                    "email": email
                },
                "session": {
                    "access_token": "mock-token",
                    "expires_at": 9999999999
                }
            }
        
        def sign_out(token: str):
            """Mock sign-out function as fallback"""
            logger.info("MOCK: Signing out user")
            return {"success": True}
