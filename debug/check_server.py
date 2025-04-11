#!/usr/bin/env python3
"""
Simple script to check if the webhook server is running
"""
import requests
import socket
import sys

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

server_ip = get_server_ip()
health_url = f"http://{server_ip}:8000/api/health"

print(f"Checking webhook server at: {health_url}")

try:
    response = requests.get(health_url, timeout=5)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response: {data}")
            print("\n✅ SUCCESS: Webhook server is running!")
        except ValueError:
            print(f"Response: {response.text}")
            print("\n⚠️ WARNING: Server is running but returned non-JSON response")
    else:
        print(f"Response: {response.text}")
        print("\n❌ ERROR: Server returned a non-200 status code")
        
except requests.ConnectionError:
    print("\n❌ ERROR: Could not connect to the server.")
    print("The webhook server doesn't appear to be running.")
    print("Start it with: python -m app.webhook_server")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    
print("\nTroubleshooting tips:")
print("1. Make sure the webhook server is running with: python -m app.webhook_server")
print("2. Check if port 8000 is already in use by another application")
print("3. Verify that your environment variables are properly configured")
print("4. Check if any firewalls are blocking the connection")