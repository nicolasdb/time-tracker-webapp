# Webhook Server Setup Guide

This guide explains how to set up and test the Time Tracker webhook server.

## Overview

The Time Tracker application consists of two main components:
1. The Streamlit web application (main UI)
2. The webhook server (for receiving device events)

These components run as separate processes. The webhook server must be running for your NFC readers to send events to the system.

## Running the Webhook Server

### Step 1: Install Dependencies

Make sure all required dependencies are installed:

```bash
pip install -r app/requirements.txt
```

### Step 2: Configure Environment Variables

The webhook server requires several environment variables to be set:

```bash
# Supabase configuration
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-anon-key"
export SUPABASE_SERVICE_KEY="your-supabase-service-key"

# Optional webhook server configuration
export WEBHOOK_PORT="8000"  # Default is 8000
export WEBHOOK_HOST="0.0.0.0"  # Default is 0.0.0.0 (all interfaces)
```

### Step 3: Start the Webhook Server

Use the provided helper script to start the webhook server:

```bash
python start_webhook_server.py
```

You should see output indicating that the server has started:
```
INFO:__main__:Starting webhook server...
INFO:__main__:Command: python -m app.webhook_server
INFO:__main__:Webhook server started.
INFO:__main__:Press Ctrl+C to stop the server.
INFO:app.webhook_server:Starting webhook server on 0.0.0.0:8000
```

### Step 4: Verify the Server is Running

You can verify that the server is running by checking the health endpoint:

```bash
python check_server.py
```

If the server is running, you should see:
```
✅ SUCCESS: Webhook server is running!
```

## Testing the Webhook

### Step 1: Create a Device and API Key

1. Open the Time Tracker web application
2. Go to the Device Management page and create a device
3. Go to the Webhook Test page and create an API key for your device

### Step 2: Validate Your API Key

Use the validation script to verify your API key is working correctly:

```bash
python validate_key.py YOUR_API_KEY_HERE
```

If successful, you'll see:
```
✅ SUCCESS: API key is valid for device: YOUR_DEVICE_ID
```

### Step 3: Send a Test Event

Use the test script to send a simulated device event:

```bash
python test_webhook.py YOUR_API_KEY_HERE YOUR_DEVICE_ID
```

If successful, you'll see:
```
✅ SUCCESS! Webhook request was successful.
```

## Troubleshooting

### 404 Not Found

This usually means the webhook server isn't running. Start it with:
```bash
python start_webhook_server.py
```

### 401 Unauthorized

This means your API key is invalid or missing. Check that:
- You're using the correct API key
- The API key is in the correct format

### 403 Forbidden

This usually means the device ID in your payload doesn't match the device ID associated with your API key. Make sure:
- The device_id field in your payload matches exactly the device ID for which the API key was created
- The device exists in your database

### Connection Refused

This means the webhook server isn't listening on the expected port. Check:
- The server is running
- No other application is using port 8000
- Your firewall isn't blocking the connection

## Server Logs

For more detailed troubleshooting, check the webhook server logs. The logs will show:
- Incoming requests
- Authentication attempts
- Database queries
- Error details

## Running in Production

For production environments:
1. Use a process manager like Supervisor or systemd to keep the webhook server running
2. Set up a reverse proxy (Nginx, Caddy) to handle HTTPS
3. Use environment variables to configure the server
4. Consider setting up monitoring for the webhook server