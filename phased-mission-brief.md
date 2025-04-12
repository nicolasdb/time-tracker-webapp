# Time Tracker Quest: Phased Mission Brief

## Phase 1: Secure HTTPS with Nginx Container

### Objective
Create a separate Nginx container that provides HTTPS for all services and acts as a reverse proxy.

### Implementation Plan
1. **Create New Repository**
   - Create a new private GitHub repo: `time-tracker-proxy`
   - Keep it lightweight with just Nginx configuration

2. **Docker Configuration**
   - Create basic `docker-compose.yml`:
     ```yaml
     version: '3'
     
     services:
       nginx:
         image: nginx:alpine
         ports:
           - "80:80"
           - "443:443"
         volumes:
           - ./nginx/conf:/etc/nginx/conf.d
           - ./certbot/conf:/etc/letsencrypt
           - ./certbot/www:/var/www/certbot
         networks:
           - web
         restart: unless-stopped
       
       certbot:
         image: certbot/certbot
         volumes:
           - ./certbot/conf:/etc/letsencrypt
           - ./certbot/www:/var/www/certbot
         depends_on:
           - nginx
         command: renew
         entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
     
     networks:
       web:
         external: true
     ```

3. **Network Setup**
   - Create external Docker network: `docker network create web`
   - Add all containers to this network:
     ```bash
     docker network connect web time-tracker-webapp
     ```

4. **Nginx Configuration**
   - Create base configuration:
     ```nginx
     server {
         listen 80;
         server_name yourdomain.com;
         server_tokens off;
     
         location /.well-known/acme-challenge/ {
             root /var/www/certbot;
         }
     
         location / {
             return 301 https://$host$request_uri;
         }
     }
     
     server {
         listen 443 ssl;
         server_name yourdomain.com;
         server_tokens off;
     
         ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
         ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
     
         # Streamlit UI on port 8501
         location / {
             proxy_pass http://time-tracker-webapp:8501;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     
         # FastAPI webhook on port 8000
         location /api/ {
             proxy_pass http://time-tracker-webapp:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```

5. **Certificate Setup**
   - First-time certificate acquisition:
     ```bash
     docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com --email your@email.com --agree-tos --no-eff-email
     ```

6. **Portainer Integration**
   - Add the stack to Portainer using the docker-compose.yml
   - Ensure the `web` network is created first
   - Configure Portainer to auto-restart the container

### Validation
- [ ] Nginx container running
- [ ] SSL certificates obtained
- [ ] HTTPS working for domain
- [ ] Traffic properly routed to Streamlit & FastAPI
- [ ] Automatic renewal configured

## Phase 2: FastAPI Webhook Server Simplification

### Objective
Create a lightweight FastAPI server with built-in testing tools and simplified authentication.

### Implementation Plan

1. **Webhook Server Basics**
   - Focus on core functionality first
   - Create `webhook_server.py` with these endpoints:
     - `GET /api/health`: Simple health check
     - `GET /api/test`: UI for testing webhooks
     - `POST /api/webhook/device-event`: Main webhook endpoint

2. **Debug Mode Toggle**
   - Add environment variable: `WEBHOOK_DEBUG=True/False`
   - When debug mode is active:
     - Log all incoming payloads
     - Accept requests without authentication
     - Show detailed error messages

3. **Testing Interface**
   - Simple HTML page at `/api/test` with:
     - Form to test webhook submissions
     - Valid payload examples
     - Response display area
     - Connection status indicator

4. **Simplified Authentication**
   - Start with a single approach: RLS-based
   - Each device is associated with a user_id
   - Validate device exists in database before processing
   - No separate API key logic yet
   
5. **Supabase Integration Testing**
   - Add explicit Supabase connection test to health endpoint
   - Display connection status in test interface
   - Log all database operations in debug mode
   - Add payload history to test interface
   
6. **Reflection Trigger Preparation**
   - Modify `tag_assignments` table schema:
     ```sql
     ALTER TABLE tag_assignments 
     ALTER COLUMN is_reflection_trigger TYPE VARCHAR DEFAULT 'none';
     ```
   - Check for reflection triggers on all incoming events:
     ```python
     # After storing event
     trigger_type = check_reflection_trigger(event.tag_id)
     if trigger_type != 'none':
         # Log trigger for stage 5 implementation
         logger.info(f"Reflection trigger detected: {trigger_type}")
         return {"status": "success", "reflection_triggered": trigger_type}
     ```

5. **Implementation**
   ```python
   from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
   from fastapi.responses import HTMLResponse
   from fastapi.staticfiles import StaticFiles
   from fastapi.templating import Jinja2Templates
   from pydantic import BaseModel
   import os
   import datetime
   import json
   from typing import Optional, List, Dict, Any
   
   # Import Supabase client
   from utils.supabase import get_supabase_client, authenticate_service_role
   
   app = FastAPI()
   
   # Store recent payloads for testing
   recent_payloads = []
   MAX_STORED_PAYLOADS = 10
   
   # Debug mode from environment
   DEBUG_MODE = os.getenv("WEBHOOK_DEBUG", "False").lower() == "true"
   
   # Templates setup
   templates = Jinja2Templates(directory="templates")
   
   # Models
   class DeviceEvent(BaseModel):
       timestamp: str
       event_type: str
       tag_present: bool
       tag_id: str
       tag_type: Optional[str] = None
       wifi_status: Optional[str] = None
       time_status: Optional[str] = None
       device_id: str
   
   # Supabase connection check
   def check_supabase_connection():
       """Test Supabase connection and return status"""
       try:
           # Try regular client first
           client = get_supabase_client()
           if client:
               # Simple query to test connection
               result = client.table('device_assignments').select('count(*)', count='exact').execute()
               device_count = result.count if hasattr(result, 'count') else 0
               return {
                   "status": "connected",
                   "client_type": "regular",
                   "device_count": device_count
               }
           
           # Try service role client
           service_client = authenticate_service_role()
           if service_client:
               result = service_client.table('device_assignments').select('count(*)', count='exact').execute()
               device_count = result.count if hasattr(result, 'count') else 0
               return {
                   "status": "connected",
                   "client_type": "service_role",
                   "device_count": device_count
               }
           
           return {"status": "disconnected", "error": "No Supabase client available"}
       except Exception as e:
           return {"status": "error", "error": str(e)}
   
   # Check if tag has reflection trigger
   def check_reflection_trigger(tag_id: str) -> str:
       """Check if tag has reflection trigger and return type"""
       try:
           client = get_supabase_client()
           service_client = authenticate_service_role()
           
           # Use service client if available, otherwise regular client
           supabase = service_client if service_client else client
           if not supabase:
               return "none"  # Can't check without client
           
           result = supabase.table('tag_assignments').select('is_reflection_trigger').eq('tag_id', tag_id).execute()
           if result and result.data and len(result.data) > 0:
               trigger_value = result.data[0].get('is_reflection_trigger')
               if trigger_value and trigger_value != 'none':
                   return trigger_value
           return "none"
       except Exception as e:
           if DEBUG_MODE:
               print(f"Error checking reflection trigger: {str(e)}")
           return "none"
   
   # Store event in database
   async def store_event(event: DeviceEvent):
       """Store event in Supabase database"""
       try:
           client = get_supabase_client()
           service_client = authenticate_service_role()
           
           # Use service client if available, otherwise regular client
           supabase = service_client if service_client else client
           if not supabase:
               return {"status": "error", "message": "No Supabase client available"}
           
           # Insert into rfid_events table
           result = supabase.table('rfid_events').insert({
               "timestamp": event.timestamp,
               "event_type": event.event_type,
               "tag_present": event.tag_present,
               "tag_id": event.tag_id,
               "tag_type": event.tag_type,
               "wifi_status": event.wifi_status,
               "time_status": event.time_status,
               "device_id": event.device_id
           }).execute()
           
           return {"status": "success", "data": result.data if hasattr(result, 'data') else None}
       except Exception as e:
           return {"status": "error", "message": str(e)}
   
   # Simple endpoints
   @app.get("/api/health")
   def health():
       # Check Supabase connection
       db_status = check_supabase_connection()
       
       return {
           "status": "healthy", 
           "timestamp": datetime.datetime.now().isoformat(), 
           "debug_mode": DEBUG_MODE,
           "database": db_status
       }
   
   # Test UI
   @app.get("/api/test", response_class=HTMLResponse)
   def test_ui(request: Request):
       # Get Supabase connection status
       db_status = check_supabase_connection()
       
       # Prepare payload history for display
       payload_history = [json.dumps(payload, indent=2) for payload in recent_payloads]
       
       return """
       <html>
           <head>
               <title>Webhook Test</title>
               <style>
                   body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                   .container { max-width: 1200px; margin: 0 auto; }
                   .panel { background: #f5f5f5; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
                   .success { color: green; }
                   .error { color: red; }
                   .warning { color: orange; }
                   pre { background: #eee; padding: 10px; border-radius: 3px; overflow: auto; }
                   button { background: #4CAF50; color: white; border: none; padding: 10px 15px; cursor: pointer; }
                   input, textarea { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; }
                   .history-item { margin-bottom: 15px; border-left: 3px solid #2196F3; padding-left: 10px; }
               </style>
           </head>
           <body>
               <div class="container">
                   <h1>Webhook Test Interface</h1>
                   
                   <div class="panel">
                       <h2>System Status</h2>
                       <p>Debug Mode: <span class="success">""" + str(DEBUG_MODE) + """</span></p>
                       <p>Database Connection: <span class=""" + ("success" if db_status["status"] == "connected" else "error") + """">""" + db_status["status"] + """</span></p>
                       """ + ("" if db_status["status"] != "connected" else "<p>Device Count: " + str(db_status.get("device_count", 0)) + "</p>") + """
                   </div>
                   
                   <div class="panel">
                       <h2>Test Webhook</h2>
                       <form id="webhookForm">
                           <label for="tagId">Tag ID:</label>
                           <input type="text" id="tagId" name="tagId" value="test-tag-001" required>
                           
                           <label for="eventType">Event Type:</label>
                           <select id="eventType" name="eventType">
                               <option value="tag_insert">Tag Insert</option>
                               <option value="tag_removed">Tag Removed</option>
                           </select>
                           
                           <label for="deviceId">Device ID:</label>
                           <input type="text" id="deviceId" name="deviceId" value="test-device-001" required>
                           
                           <label for="fullPayload">Full JSON Payload (Optional):</label>
                           <textarea id="fullPayload" name="fullPayload" rows="8">{
  "timestamp": "2025-04-11T15:23:42.000Z",
  "event_type": "tag_insert",
  "tag_present": true,
  "tag_id": "test-tag-001",
  "tag_type": "Mifare Classic",
  "wifi_status": "Connected",
  "time_status": "Synced",
  "device_id": "test-device-001"
}</textarea>
                           
                           <button type="submit">Send Test Event</button>
                       </form>
                   </div>
                   
                   <div class="panel">
                       <h2>Response</h2>
                       <pre id="response">No response yet</pre>
                   </div>
                   
                   <div class="panel">
                       <h2>Recent Payloads</h2>
                       <div id="payloadHistory">
                       """ + "".join([f'<div class="history-item"><pre>{payload}</pre></div>' for payload in payload_history]) + """
                       </div>
                   </div>
               </div>
               
               <script>
                   document.getElementById('webhookForm').addEventListener('submit', async function(e) {
                       e.preventDefault();
                       
                       const response = document.getElementById('response');
                       response.textContent = 'Sending request...';
                       
                       try {
                           // Use the full payload if provided, otherwise build from form fields
                           let payload;
                           const fullPayloadText = document.getElementById('fullPayload').value.trim();
                           
                           if (fullPayloadText) {
                               payload = JSON.parse(fullPayloadText);
                           } else {
                               payload = {
                                   timestamp: new Date().toISOString(),
                                   event_type: document.getElementById('eventType').value,
                                   tag_present: document.getElementById('eventType').value === 'tag_insert',
                                   tag_id: document.getElementById('tagId').value,
                                   tag_type: "Mifare Classic",
                                   wifi_status: "Connected",
                                   time_status: "Synced",
                                   device_id: document.getElementById('deviceId').value
                               };
                           }
                           
                           const result = await fetch('/api/webhook/device-event', {
                               method: 'POST',
                               headers: {
                                   'Content-Type': 'application/json'
                               },
                               body: JSON.stringify(payload)
                           });
                           
                           const data = await result.json();
                           response.textContent = JSON.stringify(data, null, 2);
                           
                           // Update payload history without reloading
                           const historyDiv = document.getElementById('payloadHistory');
                           const newItem = document.createElement('div');
                           newItem.className = 'history-item';
                           const pre = document.createElement('pre');
                           pre.textContent = JSON.stringify(payload, null, 2);
                           newItem.appendChild(pre);
                           historyDiv.insertBefore(newItem, historyDiv.firstChild);
                           
                       } catch (error) {
                           response.textContent = 'Error: ' + error.message;
                       }
                   });
               </script>
           </body>
       </html>
       """
   
   # Main webhook endpoint
   @app.post("/api/webhook/device-event")
   async def device_event(event: DeviceEvent, request: Request, background_tasks: BackgroundTasks):
       # Store payload in history
       global recent_payloads
       recent_payloads.insert(0, dict(event))
       if len(recent_payloads) > MAX_STORED_PAYLOADS:
           recent_payloads = recent_payloads[:MAX_STORED_PAYLOADS]
       
       if DEBUG_MODE:
           # In debug mode, log payload and always try to store it
           print(f"DEBUG MODE: Received event: {event}")
           background_tasks.add_task(store_event, event)
           
           # Check for reflection trigger
           trigger_type = check_reflection_trigger(event.tag_id)
           if trigger_type != 'none':
               print(f"DEBUG MODE: Reflection trigger detected: {trigger_type}")
               return {
                   "status": "success", 
                   "debug_mode": True,
                   "reflection_triggered": trigger_type
               }
           
           return {"status": "success", "debug_mode": True}
       
       # Production mode - validate device exists before storing
       client = get_supabase_client()
       service_client = authenticate_service_role()
       
       # Use service client if available, otherwise regular client
       supabase = service_client if service_client else client
       if not supabase:
           raise HTTPException(status_code=500, detail="Database connection error")
       
       # Check if device exists
       try:
           device_check = supabase.table('device_assignments').select('*').eq('device_id', event.device_id).execute()
           
           if not device_check.data or len(device_check.data) == 0:
               raise HTTPException(status_code=403, detail="Device not authorized")
           
           # Device exists, store the event
           storage_result = await store_event(event)
           
           if storage_result["status"] != "success":
               raise HTTPException(status_code=500, detail=f"Failed to store event: {storage_result.get('message', 'Unknown error')}")
           
           # Check for reflection trigger
           trigger_type = check_reflection_trigger(event.tag_id)
           if trigger_type != 'none':
               return {
                   "status": "success",
                   "reflection_triggered": trigger_type
               }
           
           return {"status": "success"}
           
       except HTTPException:
           raise
       except Exception as e:
           raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
   ```

### Validation
- [ ] FastAPI server runs on port 8000
- [ ] Health endpoint responds correctly
- [ ] Test interface is accessible and functional
- [ ] Debug mode properly bypasses authentication
- [ ] Webhook accepts valid payloads
- [ ] Payloads are successfully stored in Supabase
- [ ] Test page displays raw payload contents
- [ ] Supabase connection is verified in both directions (read/write)
- [ ] Reflection trigger detection is implemented and tested

## Phase 3: Streamlit UI Integration

### Objective
Improve device management in Streamlit UI and implement user-based RLS.

### Implementation Plan

1. **Device Management UI Enhancements**
   - Update `device_management.py` component
   - Remove webhook testing from Streamlit UI
   - Focus on device assignment and management

2. **User ID Assignment**
   - Automatically add current user_id to new tag/device assignments
   - Add function to get current user:
     ```python
     def get_current_user():
         # Get from Supabase auth
         client = get_supabase_client()
         if not client:
             return None
         try:
             user = client.auth.get_user()
             if user and user.id:
                 return user.id
             return None
         except Exception as e:
             logger.error(f"Failed to get current user: {str(e)}")
             return None
     ```

3. **Row-Level Security Implementation**
   - Update RLS policies in Supabase:
     ```sql
     -- Allow users to see only their devices and tags
     CREATE POLICY "Users can see their own devices"
     ON device_assignments
     FOR SELECT
     TO authenticated
     USING (user_id = auth.uid());
     
     -- Allow users to see only their tags
     CREATE POLICY "Users can see their own tags"
     ON tag_assignments
     FOR SELECT
     TO authenticated
     USING (user_id = auth.uid());
     
     -- Allow devices to insert events
     CREATE POLICY "Allow device event insertion"
     ON rfid_events
     FOR INSERT
     TO authenticated
     WITH CHECK (
       EXISTS (
         SELECT 1 FROM device_assignments
         WHERE device_assignments.device_id = rfid_events.device_id
       )
     );
     ```

4. **Device Assignment Logic**
   - Modify the device creation/update functions:
     ```python
     def create_update_device(device_data: Dict[str, Any], device_id: Optional[str] = None) -> bool:
         # Get current user
         user_id = get_current_user()
         if user_id:
             device_data['user_id'] = user_id
         
         # Rest of function remains the same
     ```

5. **Simplified Data Flow**
   - Device authentication happens through RLS policies
   - Each device must be in the device_assignments table
   - User must own the device (via user_id field)
   - No separate API key management needed

### Validation
- [ ] User ID automatically added to new devices/tags
- [ ] Users can only see their own devices/tags
- [ ] Device events are properly filtered by ownership
- [ ] Clean separation of concerns: UI for management, FastAPI for events
- [ ] Authentication works without explicit API keys

## Implementation Notes

1. **This approach simplifies authentication by leveraging Supabase RLS**
   - Uses existing user_id field for ownership
   - Avoids separate API key management
   - Each device still has a unique identifier (its UID)

2. **Debug mode provides an easy way to test and troubleshoot**
   - Switch between secured and unsecured without code changes
   - Detailed logging helps identify issues
   - Test interface makes webhook testing straightforward

3. **Phase approach allows for incremental improvement**
   - Start with security (HTTPS)
   - Then core webhook functionality
   - Then UI integration
   - Each phase builds on the previous

4. **Future expansion possibilities**
   - Could add API key management later if needed
   - Could add more sophisticated authentication
   - Could add more detailed device management

## Technical Diagrams

### Network Configuration
```
Internet (HTTPS) → Nginx Container → Internal Docker Network → Services
                                                              ↑
                                           Streamlit & FastAPI Container
```

### Authentication Flow
```
Device → Webhook → RLS Validation (device exists & has user_id) → Database
```

### UI Data Flow
```
User → Streamlit UI → Supabase Auth → RLS Filtered Data → Display
```
