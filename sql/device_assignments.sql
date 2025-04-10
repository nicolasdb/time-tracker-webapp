-- Device Assignments Table for Time Tracker Project
-- This table stores information about devices and their assignments

-- Create device_assignments table
CREATE TABLE device_assignments (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    device_id TEXT,           -- Device ID (from ESP32)
    device_name TEXT,         -- Friendly name for the device
    location TEXT,            -- Physical location of the device
    notes TEXT,               -- Additional notes about the device
    user_id UUID REFERENCES auth.users,  -- User who owns this device
    assigned_at TIMESTAMPTZ DEFAULT NOW()  -- When the assignment was created
);

-- Create index on device_id for faster lookups
CREATE INDEX idx_device_assignments_device_id ON device_assignments(device_id);

-- Enable RLS
ALTER TABLE device_assignments ENABLE ROW LEVEL SECURITY;

-- Allow full access to all authenticated users
CREATE POLICY "Full access for authenticated users"
ON device_assignments
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Function to automatically add new devices when first seen
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

-- Trigger to detect and add new devices
CREATE TRIGGER detect_new_device
AFTER INSERT ON rfid_events
FOR EACH ROW
EXECUTE FUNCTION insert_new_device();

-- Example insert for testing
INSERT INTO device_assignments (device_id, device_name, location)
VALUES ('NFC_ABC123', 'Main Entrance Reader', 'Front Door');
