# Setup Guide

This document provides instructions for setting up and running the Time Tracker application.

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/time-tracker-webapp.git
   cd time-tracker-webapp
   ```

2. **Create a .env file**
   Create a `.env` file in the `app` directory with the following variables:
   ```
   # Required Supabase credentials
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key  # Required to bypass RLS
   
   # Optional environment variables
   DEBUG_MODE=False  # Set to True to enable debug features
   WEBHOOK_DOMAIN=localhost:8000  # Used for generating webhook URLs
   WEBHOOK_PORT=8000  # Port for the FastAPI webhook service
   ```
   
   > **IMPORTANT**: The service role key is required to bypass Row Level Security (RLS) policies in Supabase. Without it, you may not see any data even if it exists in the database.

## Supabase Setup

1. **Create a Supabase Project**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Copy the URL and anon/public key for the `.env` file
   - Copy the service role key as well (found in Project Settings > API)

2. **Set up the Database Schema**
   - Navigate to the SQL Editor in your Supabase dashboard
   - Run the SQL scripts from the `sql/` directory in the following order:
     1. `rfid_events.sql` - Creates the events table
     2. `tag_assignments.sql` - Creates the tag assignments table
     3. `device_assignments.sql` - Creates the device assignments table
     4. `time_blocks_view.sql` - Creates the time blocks view
     5. `device_keys.sql` - Creates the device API keys table
     6. `rls_policies.sql` - Configures Row Level Security policies

3. **Set up Authentication**
   - In the Supabase dashboard, go to Authentication > Settings
   - Configure the Site URL to match your deployment URL (e.g., http://localhost:8501)
   - Configure any additional authentication providers if needed

## Running the Application

### Using Docker (Recommended)

```bash
docker compose up --build
```

This will start both services:
- Streamlit UI: http://localhost:8501
- Webhook API: http://localhost:8000/api/webhook/device-event
  - Health check endpoint: http://localhost:8000/api/health

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

2. **Run both services (using the entrypoint script)**
   ```bash
   cd app
   chmod +x entrypoint.sh
   ./entrypoint.sh
   ```

3. **Or run services individually**
   ```bash
   # In one terminal
   streamlit run app/streamlit_app.py

   # In another terminal
   cd app
   python -m uvicorn webhook_server:app --host 0.0.0.0 --port 8000 --reload
   ```

## Creating a Test User

To use the application, you'll need to create a user in Supabase:

1. In your Supabase dashboard, go to Authentication > Users
2. Click "Add User"
3. Enter email and password for the test user
4. Use these credentials to log in to the application

## Device Setup

To connect physical NFC reader devices:

1. Log in to the application
2. Create a device in the Device Management page
3. Go to the Webhook Test page to create an API key for your device
4. Configure your device with the webhook URL and API key
5. Test the webhook by sending a sample payload

For more details on device integration, see [WEBHOOK.md](WEBHOOK.md).

## Validation Criteria

The implementation can be validated by:

1. Successfully logging in with a Supabase user account
2. Viewing and managing tags and devices specific to the logged-in user
3. Sending test webhook events and seeing them appear in the time tracking view
4. Creating API keys and testing authentication
5. Verifying that both services (Streamlit and FastAPI) are running

## Troubleshooting

If you encounter issues:

1. **Authentication Issues**
   - Verify your Supabase credentials in the `.env` file
   - Check that the Site URL in Supabase Auth settings matches your application URL
   - Clear browser cache and try again

2. **Connection Issues**
   - Ensure your Supabase project is active
   - Check that all required tables and views are created
   - Verify network connectivity

3. **Webhook Issues**
   - Check that both services are running (ports 8501 and 8000)
   - Verify API keys are correctly configured
   - Use the Webhook Test page to validate your setup

4. **Docker Issues**
   - Check logs with `docker compose logs -f`
   - Ensure both ports are exposed and not in use by other applications
   - Try rebuilding with `docker compose down && docker compose up --build`

For more detailed troubleshooting, enable debug mode by setting `DEBUG_MODE=True` in your `.env` file.