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

## Project Structure
- `app/` - Application source code
  - `components/` - Streamlit UI components
  - `utils/` - Utility functions and helpers
- `data/` - Data storage directory (mounted volume)