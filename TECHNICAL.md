# Technical Documentation

This document provides technical details about the Time Tracker webapp implementation.

## Architecture Overview

The Time Tracker webapp is built with the following components:

1. **Streamlit Frontend**: Provides the user interface and visualization

2. **Supabase Backend**: Handles data storage and authentication

3. **Docker Containerization**: Ensures consistent deployment

## Implementation Details

### Application Services

The application now consists of one main service:

1. **Streamlit UI Service**
   - Handles user interaction and data visualization
   - Provides management interfaces for tags and devices
   - Runs on port 8501

### Application Structure

The application is organized into the following structure:

- `app/streamlit_app.py`: Streamlit application entry point

- `app/entrypoint.sh`: Script to start the service

- `app/components/`: UI components and page layouts

  - `sidebar.py`: Navigation sidebar component with authentication

  - `tag_management.py`: Tag management interface

  - `device_management.py`: Device management interface

  - `time_tracking.py`: Time tracking visualization

  - `questions.py`: Configuration utilities (debug mode)

  - `results.py`: Test results display

- `app/utils/`: Utility functions for data handling and visualization

  - `supabase.py`: Database connection management

  - `data_loader.py`: Data retrieval and formatting

  - `auth.py`: Authentication and user management

  - `visualization.py`: Chart and visualization helpers

### Authentication Implementation

The application now includes user authentication:

1. **User Authentication**
   - Implemented with Supabase Auth
   - Login/logout functionality in the UI
   - Session management using Streamlit's session state
   - Row Level Security (RLS) enforced at the database level

### Database Integration

Supabase integration is managed through the following modules:

- `app/utils/supabase.py`: Client initialization and connection handling

- `app/utils/auth.py`: Authentication and user session management

- `app/utils/data_loader.py`: Data retrieval and formatting functions

- `sql/`: SQL scripts for database setup and maintenance

  - `rfid_events.sql`: Event table setup

  - `tag_assignments.sql`: Tag assignments table

  - `device_assignments.sql`: Device assignments table

  - `time_blocks_view.sql`: Time blocks view

  - `rls_policies.sql`: Row Level Security policies

## Data Model

The data model consists of these tables and views:

```plaintext
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

```plaintext
tags
- id: UUID (PRIMARY KEY)
- tag_id: TEXT (UNIQUE, NOT NULL)
- task_category: TEXT
- task_name: TEXT
- is_reflection_trigger: BOOLEAN (DEFAULT FALSE)
- user_id: UUID (REFERENCES auth.users)
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ
```

```plaintext
devices
- id: UUID (PRIMARY KEY)
- device_id: TEXT (UNIQUE, NOT NULL)
- device_name: TEXT
- user_id: UUID (REFERENCES auth.users)
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ
```

```plaintext
time_blocks (SQL VIEW)
- tag_id: TEXT
- task_category: TEXT
- task_name: TEXT
- start_time: TIMESTAMPTZ
- end_time: TIMESTAMPTZ
- duration_minutes: FLOAT
```

The `reflections` table is planned for a future stage.

## Development Notes

### Row Level Security (RLS)

RLS is now fully implemented for all tables:

- Users can only see and manage their own data

- Service role access is available for administrative operations

RLS policies are defined in the `sql/rls_policies.sql` file and are applied to all tables.

### Multi-Service Container

The application now uses a single service container for Streamlit.

- `entrypoint.sh` script manages starting and monitoring the service

- Uses Docker health checks to ensure the service is running

- Exposes port 8501 (Streamlit)

### Data Visualization

The application supports:

- Time blocks visualization with daily tracking

- Raw RFID event display

- Tag and device management interfaces

- Dashboard with real-time metrics

- Formatted duration display (e.g., "2h 30m")

Custom visualizations are implemented using Pandas and Streamlit's native components.

### Authentication and State Management

The application uses:

- Streamlit's session state for navigation and UI state management

- Supabase Auth for user authentication

- Session refresh mechanisms for persistent login

## Stage 3 Completion

Stage 3 (Webhook Implementation & Authentication) is now complete with the following functionality:

- User authentication with Supabase Auth

- Row Level Security for data isolation

- Multi-service container architecture

### Next Steps

Stage 4 will focus on:

- Advanced time visualization dashboard

- Daily time view enhancements

- Category summaries and analytics

- Weekly overviews

- Enhanced filtering options
