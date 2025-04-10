# Technical Documentation

This document provides technical details about the Time Tracker webapp implementation.

## Architecture Overview

The Time Tracker webapp is built with the following components:

1. **Streamlit Frontend**: Provides the user interface and visualization
2. **Supabase Backend**: Handles data storage and authentication
3. **Docker Containerization**: Ensures consistent deployment

## Implementation Details

### Streamlit Application

The Streamlit application is organized into the following structure:

- `app/streamlit_app.py`: Main application entry point
- `app/components/`: UI components and page layouts
  - `sidebar.py`: Navigation sidebar component
  - `tag_management.py`: Tag management interface
  - `device_management.py`: Device management interface
  - `time_tracking.py`: Time tracking visualization
  - `questions.py`: Configuration utilities (debug mode)
  - `results.py`: Test results display
- `app/utils/`: Utility functions for data handling and visualization
  - `supabase.py`: Database connection management
  - `data_loader.py`: Data retrieval and formatting
  - `visualization.py`: Chart and visualization helpers

### Database Integration

Supabase integration is managed through the following modules:

- `app/utils/supabase.py`: Client initialization and connection handling
- `app/utils/data_loader.py`: Data retrieval and formatting functions
- `sql/`: SQL scripts for database setup and maintenance

The application supports both regular Supabase client authentication and service role authentication to bypass Row Level Security (RLS) policies when needed. Session state is used for navigation and maintaining component state across rerenders.

## Data Model

The data model consists of these tables and views:

```
rfid_events
- id: BIGINT (IDENTITY, PRIMARY KEY)
- timestamp: TIMESTAMPTZ (NOT NULL)
- event_type: TEXT (NOT NULL, 'tag_insert' or 'tag_removed')
- tag_present: BOOLEAN (NOT NULL)
- tag_id: TEXT (NOT NULL)
- tag_type: TEXT
- wifi_status: TEXT
- time_status: TEXT
- device_id: TEXT
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ
```

```
tag_assignments
- id: BIGINT (IDENTITY, PRIMARY KEY)
- tag_id: TEXT
- project_name: TEXT
- task_name: TEXT
- is_reflection_trigger: BOOLEAN (DEFAULT FALSE)
- user_id: UUID (REFERENCES auth.users)
- assigned_at: TIMESTAMPTZ
```

```
device_assignments
- id: BIGINT (IDENTITY, PRIMARY KEY)
- device_id: TEXT
- device_name: TEXT
- location: TEXT
- notes: TEXT
- user_id: UUID (REFERENCES auth.users)
- assigned_at: TIMESTAMPTZ
```

```
time_blocks (SQL VIEW)
- start_event_id: BIGINT
- end_event_id: BIGINT
- tag_id: TEXT
- project_name: TEXT
- task_name: TEXT
- start_time: TIMESTAMPTZ
- end_time: TIMESTAMPTZ
- duration_minutes: FLOAT
- activity_date: DATE
- is_reflection_trigger: BOOLEAN
- user_id: UUID
```

The `reflections` table is planned for a future stage.

## Development Notes

### Row Level Security (RLS)

To access data with RLS enabled, a service role key is required. This is specified in the `.env` file as `SUPABASE_SERVICE_KEY`. The application will attempt to use this key if regular authentication fails to retrieve data.

### Data Visualization

The application now supports:
- Time blocks visualization with daily tracking
- Raw RFID event display
- Tag and device management interfaces
- Dashboard with real-time metrics
- Formatted duration display (e.g., "2h 30m")

Custom visualizations are implemented using Pandas and Streamlit's native components, which can be extended in the `app/utils/visualization.py` and `app/components/time_tracking.py` modules.

### Navigation and State Management

The application uses Streamlit's session state for:
- Navigation between pages (stored in `st.session_state.navigation`)
- Maintaining component state (e.g., edit modes, selected items)
- Filtering and search preferences
- Form data between submissions

### Docker Configuration

The application is containerized using Docker with the following setup:
- Python 3.11 base image
- Dependencies installed from `app/requirements.txt`
- Streamlit running on port 8501
- Data mounted from the local `data/` directory

## Stage 2 Completion

Stage 2 (Data Management Interface) is now complete with the following functionality:
- Tag management with CRUD operations
- Device management with CRUD operations
- Time tracking visualization for both time blocks and raw events
- Dashboard with real-time metrics from the database
- Improved UI with better navigation and organization
- Consolidated edit/delete operations in the respective management tabs

### Next Steps

Stage 3 will focus on:
- Webhook implementation for receiving device events
- User authentication with Supabase Auth
- Row Level Security for multi-user support
- Deployment to a production server with domain name access