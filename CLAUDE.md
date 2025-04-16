# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

- Run the app locally: `streamlit run app/streamlit_app.py`
- Run with Docker: `docker compose up --build`
- Access application: `http://localhost:8501`
- Install dependencies: `pip install -r app/requirements.txt`

## Testing

- Run tests: `pytest app/tests/`
- Run a single test: `pytest app/tests/test_file.py::test_function`
- Run tests with coverage: `pytest --cov=app app/tests/`

## Code Style

- Use Python type hints for all functions
- Write docstrings for all modules, classes, and functions
- Follow Single Responsibility Principle in function design
- Use descriptive variable and function names
- Use proper error handling with try/except blocks
- Log errors with the logging module
- Keep functions focused and single-purpose
- Validate inputs before processing
- Use markdownlint for consistency in documentation

## Project Structure

- `app/` - Application source code
  - `components/` - Streamlit UI components
    - `sidebar.py` - Navigation sidebar component
    - `tag_management.py` - UI for managing RFID tags
    - `device_management.py` - UI for managing NFC reader devices
    - `time_tracking.py` - Time tracking data visualization
    - `questions.py` - Configuration questions (only shown in debug mode)
    - `results.py` - Test results display (Stage 1)
  - `utils/` - Utility functions and helpers
    - `supabase.py` - Database connection handling
    - `data_loader.py` - Data loading and query functions
    - `visualization.py` - Data visualization helpers

- `data/` - Data storage directory (mounted volume)

## Database Schema

- `rfid_events` - Raw RFID tag events (insert/remove)
- `tag_assignments` - RFID tag metadata and project assignments
  - Added fields: is_reflection_trigger, user_id
- `device_assignments` - NFC reader device metadata
  - Added field: user_id
- `time_blocks_view` - SQL view that calculates time periods between events
  - Includes validation logic to filter out false readings

## UI Navigation

- The app uses the `navigation` session state variable for page selection
- Uses a single-click navigation model with session state
- Quick action buttons on the dashboard link to relevant pages
- Current app version: v0.2.0

## Debug Mode

- Set `DEBUG_MODE=True` environment variable to enable debug information
- Debug mode shows the configuration questions at the bottom of the page
