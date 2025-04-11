#!/usr/bin/env python3
"""
Test script for the Time Tracker Webhook API
This script sends a sample RFID tag event to the webhook server.
"""
import requests
import json
import sys
import socket
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get server IP dynamically
def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be reachable
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
    print("\nExample: python test_webhook.py tk_1234abcd NFC_DEF456 tag_insert dd_54_2a_83\n")
    print("Required arguments:")
    print("  api_key   - The API key for authentication (e.g., tk_1234abcd)")
    print("  device_id - The device ID to use (e.g., NFC_DEF456)")
    print("\nOptional arguments:")
    print("  event_type - Event type: 'tag_insert' or 'tag_removed' (default: tag_insert)")
    print("  tag_id     - The RFID tag ID (default: test-tag-001)")
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

# Print request information
print(f"\n==== Webhook Test Request ====")
print(f"URL: {url}")
print(f"API Key: {API_KEY}")
print(f"Device ID: {DEVICE_ID}")
print(f"Event Type: {EVENT_TYPE}")
print(f"Tag ID: {TAG_ID}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    # Enable debug logging for requests
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    
    # Log the full request details
    logger.debug(f"URL: {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {json.dumps(payload)}")
    
    # Send the request to the webhook server with debug mode
    response = requests.post(
        url, 
        headers=headers, 
        json=payload,  # Use json parameter instead of data for proper serialization
        timeout=10
    )
    
    # Print the response
    print(f"\n==== Webhook Response ====")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    # Try to parse and display the response as JSON
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Response: {response.text}")
    
    # Print success/error message
    if 200 <= response.status_code < 300:
        print("\n✅ SUCCESS! Webhook request was successful.\n")
    else:
        print(f"\n❌ ERROR! Webhook request failed with status code {response.status_code}.\n")
        
        # Show troubleshooting tips based on the status code
        if response.status_code == 401:
            print("Troubleshooting: API key is invalid or missing")
            print("- Double-check that you're using the correct API key")
            print("- Make sure the API key is being sent in the correct format (Bearer token)")
        elif response.status_code == 403:
            print("Troubleshooting: Authentication failed or access denied")
            print("- Make sure the device_id in the payload matches the device ID linked to your API key")
            print("- Check that the device exists in your device_assignments table")
            print("- Verify that your API key is active and hasn't been deleted")
        
except Exception as e:
    print(f"\n❌ ERROR: Failed to send request: {str(e)}\n")
    print("Make sure the webhook server is running on the specified address/port.")