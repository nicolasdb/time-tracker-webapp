"""
Webhook testing component for the time tracker application.
"""
import os
import json
import logging
import streamlit as st
from datetime import datetime
import requests
from utils.supabase import get_supabase_client
from utils.auth import ensure_authenticated, get_current_user_id

# Configure logging
logger = logging.getLogger(__name__)

def test_webhook(api_key, device_id):
    """
    Test a webhook API key by sending a sample event.
    
    Args:
        api_key: The API key to test
        device_id: The device ID to use in the payload
        
    Returns:
        Tuple of (success, status_code, response_data)
    """
    try:
        # Create the test payload
        webhook_url = get_webhook_url()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "timestamp": datetime.now().isoformat() + "Z",
            "event_type": "tag_insert",
            "tag_present": True,
            "tag_id": "test-tag-001",
            "tag_type": "Mifare Classic (4-byte)",
            "wifi_status": "Connected to WiFi (-49 dBm)",
            "time_status": "Synced with NTP",
            "device_id": device_id
        }
        
        # Send the request
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=5)
        
        # Parse response
        try:
            response_data = response.json()
        except:
            response_data = response.text
            
        # Return result
        return (200 <= response.status_code < 300), response.status_code, response_data
    except Exception as e:
        logger.error(f"Error testing webhook: {str(e)}")
        return False, 0, str(e)

def generate_sample_payload():
    """Generate a sample payload for testing"""
    return {
        "timestamp": datetime.now().replace(microsecond=0).isoformat() + "Z",
        "event_type": "tag_insert",
        "tag_present": True,
        "tag_id": "dd 54 2a 83",
        "tag_type": "Mifare Classic (4-byte)",
        "wifi_status": "Connected to WiFi-2.4-6B2E (-49 dBm)",
        "time_status": "Synced with NTP",
        "device_id": "NFC_DEMO123"
    }

def get_webhook_url():
    """Get the webhook URL based on environment"""
    # For local development
    domain = os.getenv("WEBHOOK_DOMAIN", "localhost:8000")
    protocol = "https" if not domain.startswith("localhost") else "http"
    
    # Try to get the host IP
    server_ip = "localhost"
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        pass
        
    # If we're inside Docker, use the localhost
    if os.path.exists("/.dockerenv"):
        server_ip = domain.split(":")[0] if ":" in domain else domain
    
    # Return the full URL
    return f"{protocol}://{server_ip}:8000/api/webhook/device-event"

def get_device_keys(user_id):
    """Get device keys for the current user"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
            
        response = supabase.table("device_keys").select(
            "id, device_id, api_key, description, is_active, created_at"
        ).eq("user_id", user_id).execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error fetching device keys: {str(e)}")
        return []

def create_device_key(device_id, description, user_id):
    """Create a new device API key"""
    try:
        # Try with both regular client and service role client
        from utils.supabase import authenticate_service_role
        
        # First get a regular client
        supabase = get_supabase_client()
        if not supabase:
            return False, "Database connection error"
        
        # Get a service role client (has more permissions)
        service_client = authenticate_service_role()
        
        # Generate a random API key
        import secrets
        api_key = f"tk_{secrets.token_hex(16)}"
        
        # Insert the key
        data = {
            "device_id": device_id,
            "api_key": api_key,
            "description": description,
            "user_id": user_id
        }
        
        logger.info(f"Creating API key for device {device_id} and user {user_id}")
        
        # First try with service role client (more permissions)
        if service_client:
            try:
                logger.info("Attempting to create API key with service role client")
                response = service_client.table("device_keys").insert(data).execute()
                
                if response.data:
                    logger.info("API key created successfully with service role client")
                    return True, response.data[0]
            except Exception as service_error:
                logger.warning(f"Failed to create key with service role: {str(service_error)}")
        
        # If service client failed or isn't available, try with regular client
        logger.info("Attempting to create API key with regular client")
        response = supabase.table("device_keys").insert(data).execute()
        
        if response.data:
            logger.info("API key created successfully with regular client")
            return True, response.data[0]
            
        return False, "Failed to create device key"
    except Exception as e:
        logger.error(f"Error creating device key: {str(e)}")
        return False, str(e)

def delete_device_key(key_id):
    """Delete a device API key"""
    try:
        # Try with both regular client and service role client
        from utils.supabase import authenticate_service_role
        
        # First get a regular client
        supabase = get_supabase_client()
        if not supabase:
            return False, "Database connection error"
        
        # Get a service role client (has more permissions)
        service_client = authenticate_service_role()
        
        logger.info(f"Deleting API key with ID {key_id}")
        
        # First try with service role client (more permissions)
        if service_client:
            try:
                logger.info("Attempting to delete API key with service role client")
                response = service_client.table("device_keys").delete().eq("id", key_id).execute()
                
                if response:
                    logger.info("API key deleted successfully with service role client")
                    return True, None
            except Exception as service_error:
                logger.warning(f"Failed to delete key with service role: {str(service_error)}")
        
        # If service client failed or isn't available, try with regular client
        logger.info("Attempting to delete API key with regular client")
        response = supabase.table("device_keys").delete().eq("id", key_id).execute()
        
        if response:
            logger.info("API key deleted successfully with regular client")
            return True, None
            
        return False, "Failed to delete device key"
    except Exception as e:
        logger.error(f"Error deleting device key: {str(e)}")
        return False, str(e)

def get_user_devices(user_id):
    """Get devices for the current user or all devices if none found"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            logger.error("Failed to get Supabase client")
            return []
        
        # First try to get devices specifically assigned to this user
        logger.info(f"Attempting to fetch devices for user_id: {user_id}")
        response = supabase.table("device_assignments").select(
            "*"  # Select all fields to ensure we get everything we need
        ).eq("user_id", user_id).execute()
        
        # Check if we found any user-specific devices
        if response.data and len(response.data) > 0:
            logger.info(f"Found {len(response.data)} devices assigned to user {user_id}")
            return response.data
        else:
            # Log that we're fetching all devices as a fallback
            logger.info(f"No devices found for user {user_id}, fetching all available devices")
            
            # Try with service role if available
            from utils.supabase import authenticate_service_role
            service_client = authenticate_service_role()
            
            if service_client:
                # Try with service role client which has more permissions
                response = service_client.table("device_assignments").select("*").execute()
                if response.data and len(response.data) > 0:
                    logger.info(f"Found {len(response.data)} devices using service role")
                    return response.data
            
            # If service client didn't work or isn't available, try with regular client
            response = supabase.table("device_assignments").select("*").execute()
            
            devices_count = len(response.data) if response.data else 0
            logger.info(f"Fetched {devices_count} devices as fallback")
            
            # If we still have no devices, log detailed information to help debug
            if not response.data or devices_count == 0:
                # Check if the table exists and has data
                try:
                    # Try to query just the count to see if the table exists and has data
                    count_response = supabase.table("device_assignments").select("id", count="exact").execute()
                    total_count = count_response.count if hasattr(count_response, 'count') else 0
                    logger.info(f"Total device_assignments table count: {total_count}")
                except Exception as table_error:
                    logger.error(f"Error checking device_assignments table: {str(table_error)}")
                
                # Log a warning suggesting to create devices
                logger.warning("No devices found in system. Please create devices in Device Management first.")
            
            return response.data or []
    except Exception as e:
        logger.error(f"Error fetching user devices: {str(e)}")
        return []

def display_webhook_test():
    """Display the webhook testing interface"""
    if not ensure_authenticated():
        return
        
    st.title("🔗 Webhook Test")
    st.markdown("""
        Use this page to test the webhook service and configure your devices.
    """)
    
    # Get current user ID
    user_id = get_current_user_id()
    
    # Ensure we have a user ID
    if not user_id:
        st.error("Unable to get user ID. Please try logging out and back in.")
        return
    
    # Show webhook URL
    st.subheader("Webhook URL")
    webhook_url = get_webhook_url()
    st.code(webhook_url, language="bash")
    
    # API Key Management
    st.subheader("API Keys")
    st.markdown("""
        Each device needs an API key to authenticate with the webhook service.
        Create and manage your API keys below.
    """)
    
    # Get user's devices
    devices = get_user_devices(user_id)
    device_keys = get_device_keys(user_id)
    
    # Display existing keys with improved formatting
    if device_keys:
        st.markdown("#### Existing API Keys")
        
        # Create a lookup for device details
        device_details = {}
        for d in devices:
            device_details[d['device_id']] = {
                'name': d.get('device_name', 'Unnamed Device'),
                'location': d.get('location', 'No location')
            }
        
        for key in device_keys:
            # Get device details for better display
            device_id = key['device_id']
            device_info = device_details.get(device_id, {'name': 'Unknown Device', 'location': 'Unknown location'})
            
            # Create a more descriptive header for the expander
            header = f"{device_id} - {device_info['name']} ({device_info['location']}) - {key['description']}"
            
            with st.expander(header):
                cols = st.columns([3, 1])
                with cols[0]:
                    api_key_field = st.text_input(
                        "API Key", 
                        value=key['api_key'], 
                        key=f"key_{key['id']}",
                        disabled=True,
                        help="Use this key in your webhook requests"
                    )
                with cols[1]:
                    if st.button("Delete", key=f"del_{key['id']}"):
                        success, error = delete_device_key(key['id'])
                        if success:
                            st.success("API key deleted")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete key: {error}")
                            
                # Add a copy button for convenience
                st.code(f"curl -X POST \"{get_webhook_url()}\" \\\n  -H \"Content-Type: application/json\" \\\n  -H \"Authorization: Bearer {key['api_key']}\" \\\n  -d '{{\"device_id\": \"{device_id}\", ...}}'", language="bash")
                
                # Create test options
                test_cols = st.columns([1, 3])
                with test_cols[0]:
                    # Add a direct test button
                    if st.button(f"🧪 Test", key=f"test_key_{key['id']}"):
                        # Set session state for testing
                        st.session_state.testing_key = key['api_key']
                        st.session_state.testing_device = device_id
                        st.session_state.testing_id = key['id']
                        st.rerun()
                
                # Check if we're testing this key
                if hasattr(st.session_state, 'testing_key') and st.session_state.testing_id == key['id']:
                    with test_cols[1]:
                        # Test the API key
                        try:
                            test_api_key = st.session_state.testing_key
                            test_device_id = st.session_state.testing_device
                            
                            st.info(f"Testing API key for device {test_device_id}...")
                            
                            # Use our test function
                            success, status_code, response_data = test_webhook(test_api_key, test_device_id)
                            
                            # Show the result
                            if success:
                                st.success(f"✅ Success! Status code: {status_code}")
                                st.json(response_data) if isinstance(response_data, dict) else st.text(response_data)
                            else:
                                st.error(f"❌ Error! Status code: {status_code}")
                                st.json(response_data) if isinstance(response_data, dict) else st.text(response_data)
                                
                                # Provide troubleshooting guidance based on status code
                                if status_code == 404:
                                    st.warning("The webhook server isn't running. It needs to be started separately.")
                                elif status_code == 401:
                                    st.warning("Authentication failed. The API key might be invalid.")
                                elif status_code == 403:
                                    st.warning("The device ID might not match the one associated with this API key.")
                                elif "Connection refused" in str(response_data):
                                    st.warning("Connection refused. The webhook server isn't running. It needs to be started separately.")
                        except Exception as e:
                            st.error(f"❌ Error sending request: {str(e)}")
                            if "Connection refused" in str(e):
                                st.warning("Connection refused. The webhook server isn't running. It needs to be started separately.")
                        
                        # Add a clear button to stop testing
                        if st.button("Clear", key=f"clear_test_{key['id']}"):
                            if hasattr(st.session_state, 'testing_key'):
                                del st.session_state.testing_key
                            if hasattr(st.session_state, 'testing_device'):
                                del st.session_state.testing_device
                            if hasattr(st.session_state, 'testing_id'):
                                del st.session_state.testing_id
                            st.rerun()
    
    # Create new API key
    st.markdown("#### Create New API Key")
    
    if not devices:
        st.warning("You don't have any devices. Please create a device in the Device Management page first.")
        
        # Add a button to directly navigate to device management
        if st.button("Go to Device Management"):
            st.session_state.navigation = "Device Management"
            st.rerun()
            
        # Add helpful explanation
        st.info("""
        Once you create a device in the Device Management page, you'll be able to:
        1. Generate API keys for that specific device
        2. Use those keys to authenticate webhook requests
        3. Test the webhook with the curl commands provided
        
        Each device must have its own API key for security reasons.
        """)
    else:
        # Create a mapping of device IDs to existing keys
        device_key_count = {}
        for key in device_keys:
            device_id = key.get('device_id')
            if device_id not in device_key_count:
                device_key_count[device_id] = 1
            else:
                device_key_count[device_id] += 1
        
        # Create a more informative device selection dropdown
        device_options = []
        device_display_to_id = {}
        
        for d in devices:
            device_name = d.get('device_name', 'Unnamed Device')
            device_location = f" ({d.get('location', 'No location')})" if d.get('location') else ""
            key_count = device_key_count.get(d['device_id'], 0)
            key_info = f" - {key_count} existing key(s)" if key_count > 0 else ""
            display_name = f"{d['device_id']} - {device_name}{device_location}{key_info}"
            device_options.append(display_name)
            device_display_to_id[display_name] = d['device_id']
            
        with st.form("create_api_key_form"):
            selected_device_display = st.selectbox(
                "Select Device for API Key", 
                options=device_options,
                key="new_key_device_display",
                help="Select the device you want to create an API key for. The key will only work with this specific device."
            )
            
            # Convert the display name back to device_id
            device_id = device_display_to_id.get(selected_device_display)
            
            description = st.text_input(
                "Description (e.g., 'Office Device', 'Home Device')",
                key="new_key_description",
                help="Add a helpful description to remember what this API key is for"
            )
            
            st.info("This API key will be used to authenticate webhook requests from the selected device. " +
                    "You'll need to configure your physical device with this key.")
            
            submitted = st.form_submit_button("Create API Key")
            
            if submitted:
                if not device_id or not description:
                    st.error("Please fill out all fields")
                else:
                    success, result = create_device_key(device_id, description, user_id)
                    if success:
                        st.success(f"API key created successfully for device: {device_id}")
                        
                        # Store the new key in session state so we can test it after the form
                        st.session_state.new_api_key = result.get('api_key')
                        st.session_state.new_device_id = device_id
                        
                        # Refresh to show the new key in the list
                        st.rerun()
                    else:
                        st.error(f"Failed to create API key: {result}")
    
    # Check if we have a new API key to test
    if hasattr(st.session_state, 'new_api_key') and st.session_state.new_api_key:
        st.subheader("Test New API Key")
        new_key = st.session_state.new_api_key
        device_id = st.session_state.new_device_id
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🧪 Test New API Key Now"):
                with col2:
                    st.info(f"Sending test event for device {device_id} using new API key {new_key[:5]}...")
                    try:
                        # Use our test function
                        success, status_code, response_data = test_webhook(new_key, device_id)
                        
                        # Show the result
                        if success:
                            st.success(f"✅ Success! Status code: {status_code}")
                            st.json(response_data) if isinstance(response_data, dict) else st.text(response_data)
                        else:
                            st.error(f"❌ Error! Status code: {status_code}")
                            st.json(response_data) if isinstance(response_data, dict) else st.text(response_data)
                            
                            # Provide troubleshooting guidance based on status code
                            if status_code == 404:
                                st.warning("The webhook server isn't running. It needs to be started separately.")
                            elif status_code == 401:
                                st.warning("Authentication failed. The API key might be invalid.")
                            elif status_code == 403:
                                st.warning("The device ID might not match the one associated with this API key.")
                            elif "Connection refused" in str(response_data):
                                st.warning("Connection refused. The webhook server isn't running. It needs to be started separately.")
                    except Exception as e:
                        st.error(f"❌ Error sending request: {str(e)}")
                        if "Connection refused" in str(e):
                            st.warning("Connection refused. The webhook server isn't running. It needs to be started separately.")
        
        if st.button("Clear"):
            # Clear the session state
            if hasattr(st.session_state, 'new_api_key'):
                del st.session_state.new_api_key
            if hasattr(st.session_state, 'new_device_id'):
                del st.session_state.new_device_id
            st.rerun()
    
    # Sample payload
    st.subheader("Sample Payload")
    st.markdown("""
        Here's a sample payload that your device should send to the webhook URL.
        Modify this to match your device's capabilities.
    """)
    
    sample_payload = generate_sample_payload()
    st.code(json.dumps(sample_payload, indent=2), language="json")
    
    # Webhook testing instructions
    st.subheader("Testing the Webhook")
    st.markdown("""
        Follow these steps to test your webhook:
        
        1. **Select an API Key** from the list above (or create a new one)
        2. **Copy the curl command** below, replacing `YOUR_API_KEY_HERE` with your actual API key
        3. **Run the command** in your terminal
        4. **Check the Events tab** below to see if your event was recorded
    """)
    
    # Get server IP dynamically if possible
    server_ip = "localhost"
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        pass
        
    # Check if we're running in Docker
    if os.path.exists("/.dockerenv"):
        server_ip = "localhost"
        st.info(f"You're running inside Docker. Use 'localhost' or your machine's IP address if testing from outside.")
    
    # Create a better curl example with placeholder for API key
    curl_command = f"""# Replace YOUR_API_KEY_HERE with an actual API key from above
curl -X POST "http://{server_ip}:8000/api/webhook/device-event" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \\
  -d '{json.dumps(sample_payload, indent=2)}'"""
    
    st.code(curl_command, language="bash")
    
    # Add improved testing info with Python script
    with st.expander("Testing Tips & Python Script"):
        st.markdown("""
        #### Python Test Script
        
        For easier testing, we provide a Python test script you can use instead of curl. 
        Copy and save this script as `test_webhook.py`:
        """)
        
        # Python test script code
        python_script = """#!/usr/bin/env python3
import requests
import json
import sys
import socket
from datetime import datetime

# Get server IP dynamically
def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = 'localhost'
    finally:
        s.close()
    return ip

# Default values
SERVER_IP = get_server_ip()
PORT = 8000
API_KEY = None
DEVICE_ID = None
EVENT_TYPE = "tag_insert"
TAG_ID = "test-tag-001"

# Process command line arguments
if len(sys.argv) > 1:
    API_KEY = sys.argv[1]
if len(sys.argv) > 2:
    DEVICE_ID = sys.argv[2]
if len(sys.argv) > 3:
    EVENT_TYPE = sys.argv[3]
if len(sys.argv) > 4:
    TAG_ID = sys.argv[4]

# Check for required parameters
if not API_KEY or not DEVICE_ID:
    print("Usage: python test_webhook.py <api_key> <device_id> [event_type] [tag_id]")
    sys.exit(1)

# Construct the webhook URL
url = f"http://{SERVER_IP}:{PORT}/api/webhook/device-event"

# Set the headers with API key for authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Create the payload with current timestamp
payload = {
    "timestamp": datetime.now().isoformat() + "Z",
    "event_type": EVENT_TYPE,
    "tag_present": EVENT_TYPE == "tag_insert",
    "tag_id": TAG_ID,
    "tag_type": "Mifare Classic (4-byte)",
    "wifi_status": "Connected to WiFi (-49 dBm)",
    "time_status": "Synced with NTP",
    "device_id": DEVICE_ID
}

print(f"Sending webhook request to {url}")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    # Send the request to the webhook server
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {str(e)}")
"""
        st.code(python_script, language="python")
        
        st.markdown("""
        #### How to use the script
        
        1. Save the script to your computer as `test_webhook.py`
        2. Install the requests library if you don't have it: `pip install requests`
        3. Run the script with your API key and device ID:
           ```
           python test_webhook.py YOUR_API_KEY_HERE YOUR_DEVICE_ID
           ```
        4. You can also specify the event type and tag ID:
           ```
           python test_webhook.py YOUR_API_KEY_HERE YOUR_DEVICE_ID tag_insert dd_54_2a_83
           ```
        
        #### Alternative Authorization Methods
        
        The webhook supports two authorization methods:
        
        1. **Bearer Token** (recommended):
        ```
        Authorization: Bearer YOUR_API_KEY_HERE
        ```
        
        2. **X-API-Key Header**:
        ```
        X-API-Key: YOUR_API_KEY_HERE
        ```
        
        #### Common Issues
        
        - **Connection refused**: Make sure the webhook service is running on port 8000
        - **Not Found (404)**: The webhook server isn't running; start it with `python start_webhook_server.py`
        - **Unauthorized (401)**: Check that you're using a valid API key
        - **Forbidden (403)**: The device_id in the payload doesn't match the device ID associated with your API key
        - **Invalid payload**: Ensure your JSON payload matches the expected format
        
        #### Starting the Webhook Server
        
        The webhook server must be running separately from the main Streamlit app. To start it:
        
        ```bash
        # Start the webhook server in a separate terminal
        python start_webhook_server.py
        ```
        
        You can verify the server is running by checking:
        ```bash
        python check_server.py
        ```
        """)
        
    # Add a section to show recent events
    st.subheader("Recent Events")
    if st.button("Refresh Events"):
        st.rerun()
        
    try:
        supabase = get_supabase_client()
        if supabase:
            # Get recent events
            response = supabase.table("rfid_events").select(
                "*"
            ).order("created_at", desc=True).limit(5).execute()
            
            if response.data:
                for event in response.data:
                    with st.expander(f"{event['event_type']} - {event['tag_id']} - {event['created_at']}"):
                        st.json(event)
            else:
                st.info("No events found. Try sending a test event using the curl command above.")
    except Exception as e:
        st.error(f"Error fetching events: {str(e)}")
    
    # Firmware instructions
    st.subheader("Firmware Configuration")
    st.markdown("""
        When configuring your device firmware, you'll need to:
        
        1. Store the webhook URL
        2. Store the API key securely
        3. Format the payload as shown above
        4. Set the appropriate headers (`Content-Type` and `X-API-Key`)
        
        Detailed firmware instructions will be provided in a future update.
    """)
    
    st.info("For more information, check out the WEBHOOK.md file in the project repository.")