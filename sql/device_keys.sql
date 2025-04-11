-- Device Keys Table
-- Stores API keys for authenticating devices that send webhook events

-- Create the device_keys table
CREATE TABLE IF NOT EXISTS device_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  device_id TEXT NOT NULL,
  api_key TEXT NOT NULL UNIQUE,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users
);

-- Add foreign key constraint, but first check if the referenced table exists
DO $$
BEGIN
  -- First check if both tables exist
  IF EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'device_assignments' AND table_schema = 'public'
  ) THEN
    -- Try to add the foreign key constraint if it doesn't already exist
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.constraint_column_usage 
      WHERE table_name = 'device_keys' AND column_name = 'device_id'
    ) THEN
      ALTER TABLE device_keys 
      ADD CONSTRAINT fk_device_keys_device_id 
      FOREIGN KEY (device_id) 
      REFERENCES device_assignments(device_id) 
      ON DELETE CASCADE;
    END IF;
  END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_device_keys_device_id ON device_keys(device_id);
CREATE INDEX IF NOT EXISTS idx_device_keys_api_key ON device_keys(api_key);
CREATE INDEX IF NOT EXISTS idx_device_keys_user_id ON device_keys(user_id);

-- Enable Row Level Security
ALTER TABLE device_keys ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Allow users to see only their own device keys
CREATE POLICY "Users can view their own device keys" ON device_keys
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- Allow users to insert their own device keys
CREATE POLICY "Users can insert their own device keys" ON device_keys
  FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- Allow users to update their own device keys
CREATE POLICY "Users can update their own device keys" ON device_keys
  FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Allow users to delete their own device keys
CREATE POLICY "Users can delete their own device keys" ON device_keys
  FOR DELETE
  TO authenticated
  USING (user_id = auth.uid());

-- Allow service role to manage all device keys
CREATE POLICY "Service role can manage all device keys" ON device_keys
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_device_keys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update the updated_at timestamp
CREATE TRIGGER update_device_keys_updated_at_trigger
BEFORE UPDATE ON device_keys
FOR EACH ROW
EXECUTE FUNCTION update_device_keys_updated_at();

-- Function to update last_used_at when a device is authenticated
CREATE OR REPLACE FUNCTION update_device_key_last_used()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE device_keys
  SET last_used_at = NOW()
  WHERE api_key = TG_ARGV[0];
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;