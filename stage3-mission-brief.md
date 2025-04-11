# Mission Brief: Time Tracker Stage 3 Implementation

## Objective

Implement Stage 3 of the Time Tracker Quest: Create a webhook service for device events, implement user authentication, configure Row Level Security (RLS), and deploy to production - all within the existing container structure.

## Approach Overview

Rather than creating a separate repository for the webhook service, we will extend the existing codebase to create a unified solution:

- Add FastAPI to the current Python environment to handle webhook requests
- Implement both services (Streamlit UI and FastAPI webhook) in the same container
- Share configuration and environment variables between components
- Utilize a single deployment pipeline for both services

## Implementation Specifications

### 1. Project Structure Updates

```
app/
├── streamlit_app.py      # Existing Streamlit application
├── webhook_server.py     # New FastAPI webhook server
├── entrypoint.sh         # New script to run both services
├── requirements.txt      # Updated with FastAPI dependencies
├── Dockerfile            # Updated to use entrypoint.sh
└── components/           # Existing UI components
    └── ...
```

### 2. Webhook Server Implementation

Create `webhook_server.py` with the following specifications:

- Use FastAPI framework for high performance and payload validation
- Implement endpoints:
  - POST `/api/webhook/device-event` - For receiving device events
  - GET `/api/health` - For health checking
- Include authentication middleware for device payloads
- Add comprehensive error handling and logging
- Validate incoming data against expected schema
- Process events and store them in Supabase

#### Expected Payload Structure

```json
{
  "timestamp": "2025-04-11T15:23:42.000Z",
  "event_type": "tag_insert|tag_removed",
  "tag_present": true|false,
  "tag_id": "dd 54 2a 83",
  "tag_type": "Mifare Classic (4-byte)",
  "wifi_status": "Connected to WiFi-2.4-6B2E (-49 dBm)",
  "time_status": "Synced with NTP",
  "device_id": "NFC_ABC123"
}
```

### 3. Docker Configuration Updates

#### Updated Dockerfile

Update the Dockerfile to:
- Install all required dependencies
- Set up multi-process support
- Use entrypoint.sh as the entry command

#### New entrypoint.sh Script

Create a bash script that starts both services:
- Run Streamlit on port 8501
- Run FastAPI on port 8000
- Ensure proper logging for both services
- Handle graceful shutdowns

#### Updated compose.yml

Modify the Docker Compose file to:
- Expose both ports (8000 and 8501)
- Set appropriate environment variables
- Configure health checks for both services

### 4. Authentication Implementation

Implement two types of authentication:
1. **Device Authentication**
   - Simple API key validation for devices
   - Store device keys in Supabase
   - Verify device ID matches registered API key

2. **User Authentication**
   - Integrate with Supabase Auth
   - Implement login/logout in Streamlit UI
   - Add user session management
   - Configure row-level security policies

### 5. Database Schema Updates

Update the Supabase database to include:
1. New `device_keys` table to store authentication keys
2. Row-level security policies for all tables
3. User-device relationship table if needed

### 6. Documentation Updates

Update the following documentation files:
- `README.md` - Add information about webhook service
- `TECHNICAL.md` - Document the new architecture
- `project-plan.md` - Update Stage 3 implementation details
- Create new `WEBHOOK.md` - Document the webhook API and include clear instructions on how to find and use the webhook URL

### 7. Firmware Considerations

While detailed firmware development will be addressed in a future stage, add the following to support current device connectivity:

- Create a simple webhook test page in the UI that displays:
  - The current webhook URL based on deployment environment
  - A sample payload format for testing
  - Basic instructions for configuring devices

- Add a section in `WEBHOOK.md` about firmware integration:
  - How to configure devices with the correct webhook URL
  - Development vs. production URLs
  - Testing webhook connectivity

Note that comprehensive firmware development (including WiFi configuration, multi-network support, etc.) will be addressed in a dedicated future stage.

## Validation Criteria

- [ ] Webhook accepts properly formatted payloads
- [ ] Events are correctly stored in Supabase
- [ ] Invalid requests are properly rejected
- [ ] Can handle concurrent requests
- [ ] Users can securely log in/out
- [ ] User data is isolated through RLS
- [ ] All services run properly in the unified container
- [ ] Application is accessible via domain name
- [ ] Webhook URL is easily accessible for firmware configuration

## Development Process

1. Start by updating requirements.txt and Dockerfile
2. Implement the basic FastAPI webhook server
3. Create the entrypoint script to run both services
4. Test locally with simulated device payloads
5. Implement authentication mechanisms
6. Configure Row Level Security
7. Prepare for production deployment

## Production Deployment Considerations

- Domain name configuration
- HTTPS certificate setup
- Environment variable management
- Backup and monitoring solutions
- Update frequency and deployment pipeline

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Supabase Auth Documentation: https://supabase.com/docs/guides/auth
- Existing project repository structure
- Supabase RLS Documentation: https://supabase.com/docs/guides/auth/row-level-security
