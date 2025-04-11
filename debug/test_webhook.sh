#!/bin/bash

# Test webhook script
# Makes it easier to test the webhook with different parameters

# Set default values
API_KEY=""
DEVICE_ID=""
EVENT_TYPE="tag_insert"
TAG_ID="test-tag-001"

# Print usage information
usage() {
  echo "Usage: ./test_webhook.sh -k <api_key> -d <device_id> [-e <event_type>] [-t <tag_id>]"
  echo ""
  echo "Required arguments:"
  echo "  -k, --key      API key for authentication"
  echo "  -d, --device   Device ID to use"
  echo ""
  echo "Optional arguments:"
  echo "  -e, --event    Event type: 'tag_insert' or 'tag_removed' (default: tag_insert)"
  echo "  -t, --tag      RFID tag ID (default: test-tag-001)"
  echo "  -h, --help     Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./test_webhook.sh -k tk_1234abcd -d NFC_DEF456"
  echo "  ./test_webhook.sh -k tk_1234abcd -d NFC_DEF456 -e tag_removed -t dd_54_2a_83"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -k|--key)
      API_KEY="$2"
      shift 2
      ;;
    -d|--device)
      DEVICE_ID="$2"
      shift 2
      ;;
    -e|--event)
      EVENT_TYPE="$2"
      shift 2
      ;;
    -t|--tag)
      TAG_ID="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

# Validate required parameters
if [ -z "$API_KEY" ] || [ -z "$DEVICE_ID" ]; then
  echo "Error: API key and Device ID are required."
  usage
  exit 1
fi

# Make the script executable if needed
if [ ! -x ./test_webhook.py ]; then
  chmod +x ./test_webhook.py
fi

# Run the Python script with the parameters
python3 ./test_webhook.py "$API_KEY" "$DEVICE_ID" "$EVENT_TYPE" "$TAG_ID"