-- Tag Assignments Table for Time Tracker Project
-- This table stores information about RFID tags and their assignments to projects/tasks

-- Create tag_assignments table
CREATE TABLE tag_assignments (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    tag_id TEXT,             -- RFID Tag
    project_name TEXT,       -- Associated Project
    task_name TEXT,          -- Associated Task (optional)
    is_reflection_trigger BOOLEAN DEFAULT FALSE,  -- Whether this tag triggers a reflection
    user_id UUID REFERENCES auth.users,  -- User who owns this tag assignment
    assigned_at TIMESTAMPTZ DEFAULT NOW()  -- When the assignment was created
);

-- Create index on tag_id for faster lookups
CREATE INDEX idx_tag_assignments_tag_id ON tag_assignments(tag_id);

-- Enable RLS
ALTER TABLE tag_assignments ENABLE ROW LEVEL SECURITY;

-- Allow full access to all authenticated users (which is only you)
CREATE POLICY "Full access for authenticated users"
ON tag_assignments
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Function to automatically add new tags when first seen
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

-- Trigger to detect and add new tags
CREATE TRIGGER detect_new_tag
AFTER INSERT ON rfid_events
FOR EACH ROW
EXECUTE FUNCTION insert_new_tag();

-- Example insert for testing
INSERT INTO tag_assignments (tag_id, project_name, task_name)
VALUES ('dd 54 2a 83', 'Project Alpha', 'Task 1');
