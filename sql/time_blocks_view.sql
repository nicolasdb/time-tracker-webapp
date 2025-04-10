-- Time Blocks View for Time Tracker Project
-- This view calculates time blocks between tag insert and remove events
-- with filtering to handle device reading errors

DROP VIEW IF EXISTS time_blocks;

CREATE OR REPLACE VIEW time_blocks AS
SELECT 
  e1.id AS start_event_id,
  e2.id AS end_event_id,
  e1.tag_id,
  t.project_name,
  t.task_name,
  e1.timestamp AS start_time,
  e2.timestamp AS end_time,
  EXTRACT(EPOCH FROM (e2.timestamp - e1.timestamp))/60 AS duration_minutes,
  DATE(e1.timestamp) AS activity_date,
  t.is_reflection_trigger,
  t.user_id
FROM 
  rfid_events e1
JOIN 
  rfid_events e2 ON e1.tag_id = e2.tag_id AND e1.id != e2.id
LEFT JOIN
  tag_assignments t ON e1.tag_id = t.tag_id
WHERE 
  e1.event_type = 'tag_insert' AND
  e2.event_type = 'tag_removed' AND
  e2.timestamp > e1.timestamp AND
  -- Filter out intervals shorter than 30 seconds (likely errors)
  EXTRACT(EPOCH FROM (e2.timestamp - e1.timestamp)) >= 30 AND
  -- Make sure there's no other 'tag_removed' event between this pair
  NOT EXISTS (
    SELECT 1 FROM rfid_events e3
    WHERE e3.tag_id = e1.tag_id 
    AND e3.event_type = 'tag_removed'
    AND e3.timestamp > e1.timestamp 
    AND e3.timestamp < e2.timestamp
  ) AND
  -- Make sure there's no other 'tag_insert' event between this pair
  NOT EXISTS (
    SELECT 1 FROM rfid_events e4
    WHERE e4.tag_id = e1.tag_id
    AND e4.event_type = 'tag_insert' 
    AND e4.timestamp > e1.timestamp 
    AND e4.timestamp < e2.timestamp
  );

-- Notes:
-- 1. This view finds valid pairs of insert/remove events with no other events in between
-- 2. Filters out events shorter than 30 seconds (likely false readings)
-- 3. Ensures there are no other insert or remove events between each pair
-- 4. Joins with tag_assignments to get metadata about the tag
-- 5. Includes fields like is_reflection_trigger and user_id for advanced features