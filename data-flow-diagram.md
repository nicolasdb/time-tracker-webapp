# Database Structure and Data Flow

## Tables Overview

### 1. rfid_events (Raw Data)
- **Purpose**: Stores raw event data from the device
- **Population**: Direct inserts from device webhook
- **Key Fields**: timestamp, event_type, tag_id
- **Notes**: This is your event log - never modified after creation

### 2. tags (Metadata)
- **Purpose**: Maps tag IDs to meaningful activities
- **Population**: Created through UI when users categorize a tag
- **Key Fields**: tag_id, task_category, task_name, is_reflection_trigger
- **Notes**: One record per unique tag_id, created when first seen

### 3. devices (Optional)
- **Purpose**: Stores information about NFC reader devices
- **Population**: Created through UI for each device
- **Key Fields**: device_id, device_name, user_id
- **Notes**: Only needed if you have multiple devices

## Data Flow

1. **Device → Webhook → rfid_events**
   - NFC reader detects tag placement/removal
   - Sends event to webhook endpoint
   - Event stored in rfid_events table

2. **UI → tags**
   - User sees uncategorized tags in UI
   - Assigns categories and names
   - Creates/updates records in tags table

3. **rfid_events + tags → time_blocks view**
   - SQL view joins events with tag metadata
   - Calculates time blocks between insert/remove events
   - Provides foundation for time analysis

4. **time_blocks → Reflection Processing**
   - Time blocks feed into Claude-powered reflection
   - Generates insights based on categorized time data

## Visual Representation

```
┌──────────────┐       ┌───────────┐       ┌───────────────┐
│ NFC Reader   │──────▶│  Webhook  │──────▶│  rfid_events  │
└──────────────┘       └───────────┘       └───────┬───────┘
                                                   │
                                                   ▼
┌──────────────┐       ┌───────────┐       ┌───────────────┐
│  Streamlit   │◀─────▶│    UI     │◀─────▶│     tags      │
│ (User Input) │       │           │       │               │
└──────────────┘       └───────────┘       └───────┬───────┘
                                                   │
                                                   ▼
┌──────────────┐       ┌───────────┐       ┌───────────────┐
│  Reflection  │◀──────│ time_blocks│◀──────│   SQL View    │
│  Processing  │       │   view    │       │  (Join Logic) │
└──────────────┘       └───────────┘       └───────────────┘
```

## Required Payload Fields

For this system to work, your device firmware must send:
- `timestamp`: When the event occurred
- `event_type`: "tag_insert" or "tag_removed"
- `tag_id`: Unique identifier for the NFC tag
- `tag_present`: Boolean indicating if tag is present

Optional but helpful fields:
- `tag_type`: Type of NFC tag
- `wifi_status`: Current WiFi connection info
- `time_status`: NTP sync status

## Example Tag Categories

Common categories for time tracking:
- Work
- Projects
- Learning
- Exercise
- Personal
- Social
- Rest
- Administration

## Next Steps

1. Verify `rfid_events` table exists and data is flowing in
2. Create `tags` table with structure shown above
3. Build UI component to manage tag assignments
4. Create `time_blocks` view to calculate time periods
