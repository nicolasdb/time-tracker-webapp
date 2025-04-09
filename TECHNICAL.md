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
- `app/utils/`: Utility functions for data handling and visualization

### Database Integration

Supabase integration is managed through the following modules:

- `app/utils/supabase.py`: Client initialization and connection handling
- `app/utils/data_loader.py`: Data retrieval and formatting functions

The application supports both regular Supabase client authentication and service role authentication to bypass Row Level Security (RLS) policies when needed.

## Data Model

The current data model includes:

```
rfid_events (or time_events)
- id: UUID
- uid_tag: Text (NFC tag identifier)
- uid_device: Text (device identifier)
- timestamp: TIMESTAMPTZ
- event_type: Text (e.g., "tap_in", "tap_out")
- created_at: TIMESTAMPTZ
```

Additional tables as specified in the project plan will be implemented in future stages:
- devices
- tags
- reflections

## Development Notes

### Row Level Security (RLS)

To access data with RLS enabled, a service role key is required. This is specified in the `.env` file as `SUPABASE_SERVICE_KEY`. The application will attempt to use this key if regular authentication fails to retrieve data.

### Visualization

The application currently supports:
- Table views of raw and formatted data
- Bar charts of event types

Custom visualizations are implemented using Plotly and can be extended in the `app/utils/visualization.py` module.

### Docker Configuration

The application is containerized using Docker with the following setup:
- Python 3.11 base image
- Dependencies installed from `app/requirements.txt`
- Streamlit running on port 8501
- Data mounted from the local `data/` directory

## Stage 1 Completion

Stage 1 (Foundation) is now complete with the following functionality:
- Streamlit application running in Docker container
- Supabase connection with RLS bypass capability
- Basic UI layout with navigation and configuration
- Data retrieval and visualization of RFID events

### Next Steps

Stage 2 will focus on implementing the data management interface, including:
- Tag management
- Device management
- CRUD operations
- User authentication