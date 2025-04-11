# Webhook API Documentation

This document provides information about the webhook service for the Time Tracker application.

## Overview

The Time Tracker application includes a webhook service that receives and processes events from NFC reader devices. This webhook service:

- Receives events when tags are inserted or removed from NFC readers
- Authenticates devices using API keys
- Validates the payload format
- Stores events in the Supabase database
- Provides health check endpoints

## Webhook Endpoints

### Health Check

```
GET /api/health
```

Use this endpoint to check if the webhook service is running properly. It doesn't require authentication.

**Sample response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2025-04-11T15:23:42.000Z"
}
```

### Device Event

```
POST /api/webhook/device-event
```

Use this endpoint to send device events when tags are inserted or removed from NFC readers.

**Headers:**
- `Content-Type: application/json` (required)
- One of the following for authentication:
  - `X-API-Key: YOUR_API_KEY_HERE` or
  - `Authorization: Bearer YOUR_API_KEY_HERE`

**Request Body Format:**
```json
{
  "timestamp": "2025-04-11T15:23:42.000Z",
  "event_type": "tag_insert",
  "tag_present": true,
  "tag_id": "dd 54 2a 83",
  "tag_type": "Mifare Classic (4-byte)",
  "wifi_status": "Connected to WiFi-2.4-6B2E (-49 dBm)",
  "time_status": "Synced with NTP",
  "device_id": "NFC_ABC123"
}
```

**Field descriptions:**
- `timestamp`: ISO 8601 formatted timestamp with timezone (required)
- `event_type`: Either "tag_insert" or "tag_removed" (required)
- `tag_present`: Boolean indicating if a tag is present (required)
- `tag_id`: The ID of the RFID tag (required)
- `tag_type`: The type of RFID tag (optional)
- `wifi_status`: Current WiFi connection status (optional)
- `time_status`: Time synchronization status (optional)
- `device_id`: The unique identifier for the device (required)

**Sample response (success):**
```json
{
  "status": "success",
  "message": "Event stored successfully"
}
```

**Sample response (error):**
```json
{
  "status": "error",
  "message": "Error message details"
}
```

## Authentication

The device event endpoint requires authentication using API keys. Each device must have an API key that is used for authentication.

Two authentication methods are supported:
1. API Key Header: Send the key in the `X-API-Key` header
2. Bearer Token: Send the key in the `Authorization` header as `Bearer YOUR_API_KEY_HERE`

### API Key Management

API keys can be managed in the Webhook Test page of the Time Tracker web application. This page allows you to:

1. View existing API keys for each device
2. Create new API keys by selecting a specific device from a dropdown
3. Test API keys directly from the web interface
4. Delete API keys that are no longer needed

**Important**: The API key is bound to a specific device ID. When sending events, the `device_id` field in the request payload must match the device ID associated with the API key. If they don't match, the request will be rejected.

### API Key Security

The API key system is designed with these security considerations:

1. Each physical device should have its own unique API key
2. API keys are linked to specific devices and can't be used with other devices
3. Keys can be revoked at any time by deleting them
4. New keys can be generated if a key is compromised
5. The system validates both the API key and the device ID in each request

## Finding the Webhook URL

The webhook URL depends on your deployment environment:

- **Local Development**: `http://localhost:8000/api/webhook/device-event`
- **Production**: `https://your-domain.com/api/webhook/device-event`

You can find the correct URL for your environment in the Webhook Test page of the Time Tracker web application.

## Testing API Key Validation

Before sending actual events, you can validate that your API key is working correctly:

```bash
# Using the validation endpoint
curl -X GET "http://localhost:8000/api/webhook/validate-key" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"
```

If the key is valid, you'll receive a response like:

```json
{
  "status": "success",
  "message": "API key is valid",
  "device_id": "YOUR_DEVICE_ID",
  "timestamp": "2025-04-11T15:23:42.000Z"
}
```

We also provide validation scripts in the repository that make testing easier:

```bash
# Validate an API key
python validate_key.py YOUR_API_KEY_HERE
```

## Testing the Webhook

### Using the Web Interface

The easiest way to test the webhook is using the built-in testing feature in the Webhook Test page:

1. Go to the Webhook Test page in the application
2. Under "Existing API Keys", find the key you want to test 
3. Click the "Test" button next to that key
4. View the test results directly in the interface

### Using curl Command

You can also test the webhook using curl or any HTTP client:

```bash
# Using X-API-Key header
curl -X POST "http://localhost:8000/api/webhook/device-event" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "timestamp": "2025-04-11T15:23:42.000Z",
    "event_type": "tag_insert",
    "tag_present": true,
    "tag_id": "dd 54 2a 83",
    "tag_type": "Mifare Classic (4-byte)",
    "wifi_status": "Connected to WiFi-2.4-6B2E (-49 dBm)",
    "time_status": "Synced with NTP",
    "device_id": "NFC_YOUR_DEVICE_ID"
  }'

# OR using Bearer token in Authorization header
curl -X POST "http://localhost:8000/api/webhook/device-event" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "timestamp": "2025-04-11T15:23:42.000Z",
    "event_type": "tag_insert",
    "tag_present": true,
    "tag_id": "dd 54 2a 83",
    "tag_type": "Mifare Classic (4-byte)",
    "wifi_status": "Connected to WiFi-2.4-6B2E (-49 dBm)",
    "time_status": "Synced with NTP",
    "device_id": "NFC_YOUR_DEVICE_ID"
  }'
```

Replace `YOUR_API_KEY_HERE` with your actual API key and `NFC_YOUR_DEVICE_ID` with your device ID.

### Using the Python Script

For more advanced testing, the application provides Python scripts:

```bash
# Test a specific API key with its associated device
python test_webhook.py YOUR_API_KEY_HERE YOUR_DEVICE_ID
```

### Important Testing Notes

When testing, remember these key points:

1. The webhook server must be running (it's a separate process from the main application)
2. The device ID in your payload must match the device ID associated with the API key
3. Common errors include 404 (server not running), 401 (invalid API key), and 403 (device ID mismatch)

## Firmware Integration

When integrating the webhook with your device firmware, consider the following:

### 1. Configuration Storage

The firmware should store:
- Webhook URL
- API key
- Device ID

Ideally, these should be configurable via a web interface or similar mechanism.

### 2. Event Triggering

The firmware should trigger events when:
- A tag is inserted (detected)
- A tag is removed (no longer detected)

### 3. Error Handling

The firmware should handle various error conditions:
- Network connectivity issues
- Authentication failures
- Server errors

Implement retry logic with exponential backoff for transient failures.

### 4. Development vs. Production

Use different webhook URLs for development and production environments:
- Development: `http://localhost:8000/api/webhook/device-event`
- Production: `https://your-domain.com/api/webhook/device-event`

### 5. Testing

Before deploying to production, test your firmware with:
- The webhook test endpoint
- Various error conditions
- Different network scenarios

## Troubleshooting

If you encounter issues with the webhook service:

### Common Errors

| Status Code | Meaning | Troubleshooting |
|-------------|---------|-----------------|
| 404 Not Found | The webhook server is not running | Start the webhook server separately from the main app |
| 401 Unauthorized | Invalid or missing API key | Verify that you're using the correct API key |
| 403 Forbidden | Device ID mismatch | Make sure the device ID in your payload matches the one associated with the API key |
| Connection refused | Server not listening on the expected port | Check that the webhook server is running on port 8000 |

### Webhook Server Status

To check if the webhook server is running, try accessing the health endpoint:

```bash
curl http://localhost:8000/api/health
```

If successful, you should receive a response like:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2025-04-11T15:23:42.000Z"
}
```

### Key Validation

To test if your API key is valid without sending a full event:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" http://localhost:8000/api/webhook/validate-key
```

### Payload Validation

Ensure your payload matches the expected format:
- All required fields are present
- Timestamp is in ISO 8601 format
- event_type is either "tag_insert" or "tag_removed"
- device_id matches the one associated with your API key

For more detailed error investigation, check the application logs for more information.

For more assistance, contact your system administrator.

## Future Enhancements

Planned enhancements for the webhook service include:

- Webhook event logging UI
- Enhanced error reporting
- Device firmware configuration UI
- Support for additional event types
- Real-time status monitoring

Stay tuned for updates in future releases.