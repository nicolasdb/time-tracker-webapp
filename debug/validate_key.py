#!/usr/bin/env python3
"""
Validate API key script for the Time Tracker Webhook API.
This script checks if your API key is valid without sending an event.
"""
import requests
import json
import sys
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
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

# Check if API key is provided
if len(sys.argv) < 2:
    print("Usage: python validate_key.py <api_key>")
    print("Example: python validate_key.py tk_1234abcd")
    sys.exit(1)

# Get API key from command line
api_key = sys.argv[1]

# Construct the validation URL
server_ip = get_server_ip()
validation_url = f"http://{server_ip}:8000/api/webhook/validate-key"

# Set the headers with API key for authentication
headers = {
    "Authorization": f"Bearer {api_key}"
}

print(f"\n🔑 Validating API key: {api_key[:5]}{'*' * (len(api_key) - 5)}")
print(f"URL: {validation_url}")

try:
    # Send the validation request
    response = requests.get(validation_url, headers=headers, timeout=10)
    
    print(f"\n==== Validation Response ====")
    print(f"Status Code: {response.status_code}")
    
    # Parse response
    try:
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS: API key is valid for device: {response_data.get('device_id', 'unknown')}")
        else:
            print(f"\n❌ ERROR: API key validation failed with status code {response.status_code}")
            print("Details:", response_data.get('detail', 'No details provided'))
    except ValueError:
        print(f"Response: {response.text}")
        print(f"\n❌ ERROR: Could not parse response as JSON")

except Exception as e:
    print(f"\n❌ ERROR: Request failed: {str(e)}")
    print("Make sure the webhook server is running on the specified address/port.")

print("\n============================")
print("Troubleshooting tips if validation failed:")
print("1. Check if the webhook server is running (try http://localhost:8000/api/health)")
print("2. Verify that the API key exists in the database")
print("3. Try creating a new API key in the Webhook Test page")
print("4. Check if the SUPABASE_SERVICE_KEY is set correctly in your environment")
print("5. Check the server logs for more detailed error messages")
print("============================\n")