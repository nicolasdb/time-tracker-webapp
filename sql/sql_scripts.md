# SQL Scripts for Time Tracker Project

This document describes the SQL scripts used to set up the database structure for the Time Tracker project and provides step-by-step instructions for configuring Supabase.

## Database Structure Overview

The project uses three main tables:

1. **rfid_events** - Records all RFID tag events (insertion/removal)
2. **tag_assignments** - Links RFID tags to projects and tasks
3. **device_assignments** - Tracks device information and locations
4. **time_blocks_view** - SQL view that calculates time spent on activities

## SQL Scripts

### 1. rfid_events.sql

The primary table for storing all RFID tag events:

- Records tag insertions and removals with timestamps
- Stores tag IDs, types, and device IDs
- Includes WiFi and time sync status information

### 2. tag_assignments.sql

Links RFID tags to projects and tasks:

- Automatically adds new tags when first detected (via trigger)
- Allows for organizing tags by project and task
- Includes `is_reflection_trigger` flag to identify tags that should trigger reflection
- Links tags to specific users via `user_id` field

### 3. device_assignments.sql

Tracks information about physical devices:

- Stores friendly names, locations, and notes for each device
- Automatically adds new devices when first detected (via trigger)

### 4. time_blocks_view.sql

SQL view that calculates time blocks from tag events:

- Joins insert and remove events to calculate duration
- Links events with tag metadata for meaningful reporting
- Filters out potential false readings (events shorter than 30 seconds)
- Implements robust logic to handle reading errors:
  - Ensures no other events exist between a valid insert/remove pair
  - Handles missing insert or remove events by ignoring them 
  - Stores event IDs for referencing specific readings
- Includes user_id and is_reflection_trigger fields for advanced features
- Adds activity_date field for easy date-based filtering

## Supabase Setup Guide

### Step 1: Create a Supabase Project

1. Go to [Supabase](https://supabase.com/) and sign in
2. Create a new project with a name like "Time-Tracker"
3. Note your project URL and API keys (you'll need these later)

### Step 2: Set Up Database Tables

Execute the SQL scripts in the following order:

1. First, run `rfid_events.sql` to create the main events table
   - Validation: Check that the table appears in the Supabase Table Editor
   - Validation: Verify indexes are created (check "Indexes" in Table Editor)

2. Next, run `tag_assignments.sql` to create the tag assignments table and trigger
   - Validation: Check that the table appears in the Table Editor
   - Validation: Verify the trigger is created (check "Triggers" in Database section)

3. Run `device_assignments.sql` to create the device assignments table and trigger
   - Validation: Check that the table appears in the Table Editor
   - Validation: Verify the trigger is created

4. Create the `time_blocks_view.sql` view
   - Validation: Check that the view appears in the Table Editor under "Views"

### Step 3: Updating Existing Tables (If Already Created)

If you have already set up the tables and need to add the new fields:

1. Go to Supabase SQL Editor
2. Execute the following SQL to update tag_assignments:

```sql
-- Add is_reflection_trigger field
ALTER TABLE tag_assignments ADD COLUMN IF NOT EXISTS is_reflection_trigger BOOLEAN DEFAULT FALSE;

-- Add user_id field with reference to auth.users
ALTER TABLE tag_assignments ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users;

-- Update trigger function to handle new fields
CREATE OR REPLACE FUNCTION insert_new_tag()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if tag_id already exists in tag_assignments
    IF NOT EXISTS (SELECT 1 FROM tag_assignments WHERE tag_id = NEW.tag_id) THEN
        INSERT INTO tag_assignments (tag_id, is_reflection_trigger, user_id)
        VALUES (NEW.tag_id, FALSE, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

3. Execute the following SQL to update device_assignments:

```sql
-- Add user_id field with reference to auth.users
ALTER TABLE device_assignments ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users;

-- Update trigger function to handle new fields
CREATE OR REPLACE FUNCTION insert_new_device()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if device_id already exists in device_assignments
    IF NOT EXISTS (SELECT 1 FROM device_assignments WHERE device_id = NEW.device_id) THEN
        INSERT INTO device_assignments (device_id, user_id)
        VALUES (NEW.device_id, NULL);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

4. Create or update the time_blocks view
   
   After adding the columns, run the SQL in the `time_blocks_view.sql` file to create or update the view.

### Step 4: Configure n8n Integration

1. Get Supabase Service Role Key:
   - Go to your Supabase project dashboard
   - Navigate to Project Settings -> API
   - Copy the `service_role` key (starts with `eyJ...`)
   - This key bypasses RLS and has full access to the database

2. Configure n8n Workflow:

   ```txt
   Webhook Node -> Supabase Node
   ```

3. Supabase Node Configuration:
   - Add new credentials
     - Host: Your Supabase project URL (e.g., `https://xxxxxxxxxxxx.supabase.co`)
     - Service Role Key: Paste the key from step 1
     - Name these credentials (e.g., "RFID-Supabase")
   - Operation: Insert
   - Table: rfid_events
   - Data Mapping (from webhook payload):

     ```txt
     {
       "timestamp": "{{$json.rfid_poll_result.timestamp}}",
       "event_type": "{{$json.rfid_poll_result.event_type}}",
       "tag_present": "{{$json.rfid_poll_result.tag_present}}",
       "tag_id": "{{$json.rfid_poll_result.tag_id}}",
       "tag_type": "{{$json.rfid_poll_result.tag_type}}",
       "wifi_status": "{{$json.rfid_poll_result.wifi_status}}",
       "time_status": "{{$json.rfid_poll_result.time_status}}",
       "device_id": "{{$json.rfid_poll_result.device_id}}"
     }
     ```

### Step 4: Test the Integration

1. Deploy the ESP32 firmware with the webhook URL pointing to your n8n instance
2. Scan an RFID tag with the device
3. Verify data flow:
   - Check that events appear in the `rfid_events` table
   - Verify that new tags are automatically added to `tag_assignments`
   - Verify that new devices are automatically added to `device_assignments`

## Database Design Notes

- **Row Level Security (RLS)**: All tables have RLS enabled with policies that allow authenticated users full access
- **Automatic Timestamps**: The `rfid_events` table has automatic handling for `created_at` and `updated_at`
- **Triggers**: Both `tag_assignments` and `device_assignments` have triggers that automatically add new entries
- **Indexes**: All tables have indexes on key columns for efficient querying
- **Data Types**: Uses PostgreSQL-specific types like `TIMESTAMPTZ` for proper timezone handling

## Maintenance and Troubleshooting

### Fixing NULL or Empty device_id Entries

If you have device_assignments entries with NULL or empty device_id values (which can happen from manual entries or other sources), you can clean them up with:

```sql
-- Option 1: Delete all NULL or empty device_id entries
DELETE FROM device_assignments 
WHERE device_id IS NULL OR device_id = '';

-- Option 2: Update NULL or empty entries with a placeholder
UPDATE device_assignments 
SET device_id = 'MANUAL_ENTRY_' || id::text
WHERE device_id IS NULL OR device_id = '';
```

### Modifying Triggers

If you need to modify a trigger function:

  1. First, drop the existing trigger:

   ```sql
   DROP TRIGGER trigger_name ON table_name;
   ```

  1. Then, update the function and recreate the trigger:

   ```sql
   CREATE OR REPLACE FUNCTION function_name() ... 
   CREATE TRIGGER trigger_name ...
   ```

### Backing Up Data

To back up your data from Supabase:

1. Go to Project Settings -> Database
2. Click "Database Backups"
3. Download the latest backup or create a new one
