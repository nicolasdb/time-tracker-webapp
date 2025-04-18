# TIME TRACKER QUEST: PROJECT PLAN

## Project Overview

Building a time tracking system that uses physical NFC interactions to log activities, stores data in Supabase, and generates reflective insights. This system forms the foundation of the Cognitive Wealth System's first phase implementation.

## Architecture Components

1. **Time Tracker Device** - Physical NFC reader sending event data

2. **Supabase Database** - Stores all time tracking and user data

3. **Web UI (Streamlit)** - Dashboard for data visualization and management

4. **Processing Service** - Generates reflections based on time data

5. **Email Service** - Delivers reflections to users

## Development Stages & Validation Criteria

### Stage 1: Foundation - Streamlit + Supabase Connection ✅

**Objective**: Create a basic dashboard that can connect to Supabase and display data.

**Tasks**:

- [x] Set up Streamlit container with Docker

- [x] Configure Supabase connection

- [x] Create basic UI layout

- [x] Implement test data display

**Validation Criteria**:

- ✓ Streamlit app runs successfully in container

- ✓ App connects to Supabase without errors

- ✓ Test queries return expected results

- ✓ Basic data visualization works

**Notes**:

- Row Level Security (RLS) access implemented using service role key

- Data visualization and formatting for RFID events working

- Added debugging panel for troubleshooting database connections

- Completed: April 9, 2025

- Cost Claude: 2.50€

### Stage 2: Data Management Interface

**Objective**: Build UI for managing tags, devices, and users.

**Tasks**:

- [x] Create tag management interface

- [x] Create device management interface

- [x] Implement CRUD operations for tags

- [x] Implement CRUD operations for devices

- [x] Implement time tracking visualization

**Validation Criteria**:

- ✓ Can create, read, update, and delete tags

- ✓ Can assign categories and names to tags

- ✓ Can manage device information

- ✓ Authentication protects private data

**Notes**:

- Database enhancements included adding user_id and reflection trigger fields

- Time blocks view implemented with robust error handling for device reading issues

- Complete tag and device management interfaces with CRUD operations

- Time tracking visualization for both blocks and raw events

- Integrated real-time metrics into dashboard

- Improved UI navigation and workflow

- Completed: April 10, 2025

- Duration: 3h 25m (wall time), 18m 32s (API time)

- Cost: $6.05

### Stage 3: Webhook Implementation & Authentication ✅

**Objective**: Build service to receive and process device payloads and implement user authentication.

**Tasks**:

- [x] Create webhook service container

- [x] Implement endpoint for device events

- [x] Add validation and error handling

- [x] Configure secure communication

- [x] Implement user authentication with Supabase Auth

- [x] Add login/logout functionality

- [x] Configure Row Level Security for user data

- [x] Create device API key management

- [x] Implement device-specific API keys

- [x] Add support for multiple authentication methods

- [x] Create validation endpoint for easier testing

- [x] Implement service role authentication for admin functions

- [x] Document webhook integration for devices

**Validation Criteria**:

- ✓ Webhook accepts properly formatted payloads

- ✓ Events are correctly stored in Supabase

- ✓ Invalid requests are properly rejected

- ✓ Can handle concurrent requests

- ✓ Users can securely log in/out

- ✓ User data is isolated through RLS

- ✓ Webhook provides clear testing interface

- ✓ API keys are securely managed

- ✓ Device-specific API keys enforce security

- ✓ Multiple authentication methods supported

- ✓ Testing tools provide clear feedback

**Notes**:

- Implemented unified container approach with both services in one container

- Added FastAPI for high-performance webhook processing

- Created comprehensive authentication system for both users and devices

- Implemented device API key management with device-specific keys

- Added support for both Bearer token and X-API-Key authentication methods

- Added detailed webhook testing interface with direct testing capabilities

- Created new database table for device keys with proper foreign key relationships

- Added validation endpoint to check API keys without sending events

- Added RLS policies for all tables with service role bypass for admin functions

- Created helper scripts for webhook testing and validation

- Updated documentation including new WEBHOOK.md guide with troubleshooting section

- Improved error handling and feedback for webhook requests

- Completed: April 11, 2025

- Duration: 3h 50m (wall time), 38m 4s (API time)

- Cost: $14.29

### Stage 4: Time Visualization Dashboard

**Objective**: Create visualizations of time tracking data.

**Tasks**:

- [ ] Implement daily time view

- [ ] Add category summaries

- [ ] Create weekly overview

- [ ] Add filtering options

**Validation Criteria**:

- ✓ Visualizations accurately represent time data

- ✓ Summaries calculate correctly

- ✓ Filters work as expected

- ✓ UI remains responsive with larger datasets

### Stage 5: Reflection Processing

**Objective**: Implement Claude-powered reflections on time data.

**Tasks**:

- [ ] Set up Processing Service

- [ ] Integrate Claude API

- [ ] Create reflection triggers

- [ ] Implement email delivery

**Validation Criteria**:

- ✓ Processing Service generates meaningful reflections

- ✓ Reflections incorporate time data correctly

- ✓ Triggers work reliably

- ✓ Emails are delivered successfully

## Database Schema

```sql
-- Main Tables
CREATE TABLE rfid_events (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('tag_insert', 'tag_removed')),
    tag_present BOOLEAN NOT NULL,
    tag_id TEXT NOT NULL,
    tag_type TEXT,
    wifi_status TEXT,
    time_status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_rfid_events_timestamp ON rfid_events(timestamp);
CREATE INDEX idx_rfid_events_tag_id ON rfid_events(tag_id);
CREATE INDEX idx_rfid_events_event_type ON rfid_events(event_type);

-- Enable Row Level Security (RLS)
ALTER TABLE rfid_events ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts from webhook
CREATE POLICY "Enable insert for webhooks" ON rfid_events
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create policy to allow read access
CREATE POLICY "Enable read access for authenticated users" ON rfid_events
    FOR SELECT
    TO authenticated
    USING (true);

CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id TEXT UNIQUE NOT NULL,
  device_name TEXT,
  user_id UUID REFERENCES auth.users,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tag_id TEXT UNIQUE NOT NULL,
  task_category TEXT,
  task_name TEXT,
  is_reflection_trigger BOOLEAN DEFAULT FALSE,
  user_id UUID REFERENCES auth.users,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reflections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users,
  content TEXT,
  reflection_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Views (to be created)
CREATE VIEW time_blocks AS
SELECT 
  e1.tag_id,
  t.task_category,
  t.task_name,
  e1.timestamp AS start_time,
  e2.timestamp AS end_time,
  EXTRACT(EPOCH FROM (e2.timestamp - e1.timestamp))/60 AS duration_minutes
FROM 
  rfid_events e1
JOIN 
  rfid_events e2 ON e1.tag_id = e2.tag_id AND e1.id != e2.id
LEFT JOIN
  tags t ON e1.tag_id = t.tag_id
WHERE 
  e1.event_type = 'tag_insert' AND
  e2.event_type = 'tag_removed' AND
  e2.timestamp > e1.timestamp AND
  NOT EXISTS (
    SELECT 1 FROM rfid_events e3
    WHERE e3.tag_id = e1.tag_id 
    AND e3.timestamp > e1.timestamp 
    AND e3.timestamp < e2.timestamp
  );
```

## Testing Strategy

### Unit Testing

- Test Supabase connection and queries

- Test webhook payload processing

- Test data transformation functions

### Integration Testing

- Test full data flow from webhook to database

- Test reflection generation with real data

- Test email delivery pipeline

### User Acceptance Testing

- Verify UI is intuitive and responsive

- Ensure visualizations are meaningful

- Confirm reflection quality meets expectations

## Deployment Architecture

```plaintext
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Webhook Service │     │  Streamlit UI   │     │ Processing Svc  │
│  (Docker/Flask) │     │  (Docker/Py)    │     │  (Docker/Py)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────┬───────┴───────────────┬───────┘
                         │                       │
                  ┌──────┴───────┐       ┌──────┴───────┐
                  │   Supabase   │       │ Email Service│
                  │  Database    │       │  (SendGrid)  │
                  └──────────────┘       └──────────────┘
```

## Flow State Optimization

Following your preference for flow states, the implementation approach prioritizes:

1. **Minimal Context Switching** - Complete one component before moving to next

2. **Immediate Feedback** - Create test cases that provide quick validation

3. **Clear Decision Points** - Each stage has explicit validation criteria

4. **Simple Rules** - Following the "elegantly simple" principle from your framework

## Implementation Notes

- Use Python 3.9+ for all services

- Streamlit for rapid UI development

- Supabase for authentication and database

- Docker for containerization and deployment

- Flask for lightweight webhook service

- SendGrid for email delivery (optional)

## Next Steps

1. Set up project repository structure

2. Configure Docker for local development

3. Begin Stage 1 implementation
