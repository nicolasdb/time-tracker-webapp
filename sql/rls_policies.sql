-- Row Level Security Policies for Time Tracker Tables
-- This script adds or updates RLS policies for all tables

-- Enable RLS on all tables
ALTER TABLE IF EXISTS rfid_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS device_assignments ENABLE ROW LEVEL SECURITY;

-- RFID Events Table Policies
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Enable insert for webhooks" ON rfid_events;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON rfid_events;
DROP POLICY IF EXISTS "Users can view events from their devices" ON rfid_events;

-- 1. Allow authenticated webhook API to insert events
CREATE POLICY "Enable insert for authenticated webhook" ON rfid_events
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- 2. Allow users to view only their own devices' events
CREATE POLICY "Users can view events from their devices" ON rfid_events
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM device_assignments
      WHERE device_assignments.device_id = rfid_events.device_id
      AND device_assignments.user_id = auth.uid()
    )
  );

-- 3. Allow service role to access all events
CREATE POLICY "Service role can manage all events" ON rfid_events
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Tags Table Policies
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own tags" ON tags;
DROP POLICY IF EXISTS "Users can insert their own tags" ON tags;
DROP POLICY IF EXISTS "Users can update their own tags" ON tags;
DROP POLICY IF EXISTS "Users can delete their own tags" ON tags;

-- 1. Allow users to view only their own tags
CREATE POLICY "Users can view their own tags" ON tags
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- 2. Allow users to insert their own tags
CREATE POLICY "Users can insert their own tags" ON tags
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- 3. Allow users to update their own tags
CREATE POLICY "Users can update their own tags" ON tags
  FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 4. Allow users to delete their own tags
CREATE POLICY "Users can delete their own tags" ON tags
  FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- 5. Allow service role to manage all tags
CREATE POLICY "Service role can manage all tags" ON tags
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Device Assignments Table Policies
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own devices" ON device_assignments;
DROP POLICY IF EXISTS "Users can insert their own devices" ON device_assignments;
DROP POLICY IF EXISTS "Users can update their own devices" ON device_assignments;
DROP POLICY IF EXISTS "Users can delete their own devices" ON device_assignments;

-- 1. Allow users to view only their own devices
CREATE POLICY "Users can view their own devices" ON device_assignments
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- 2. Allow users to insert their own devices
CREATE POLICY "Users can insert their own devices" ON device_assignments
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- 3. Allow users to update their own devices
CREATE POLICY "Users can update their own devices" ON device_assignments
  FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 4. Allow users to delete their own devices
CREATE POLICY "Users can delete their own devices" ON device_assignments
  FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- 5. Allow service role to manage all devices
CREATE POLICY "Service role can manage all devices" ON device_assignments
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);