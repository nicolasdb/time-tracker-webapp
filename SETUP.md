# Setup Guide

This document provides instructions for setting up and running the Time Tracker application.

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/time-tracker-webapp.git
   cd time-tracker-webapp
   ```

2. **Create a .env file**
   Create a `.env` file in the project root with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   SUPABASE_SERVICE_KEY=your_supabase_service_role_key  # Required to bypass RLS
   ```
   
   > **IMPORTANT**: The service role key is required to bypass Row Level Security (RLS) policies in Supabase. Without it, you may not see any data even if it exists in the database.

## Supabase Setup

1. **Create a Supabase Project**
   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project
   - Copy the URL and anon/public key for the `.env` file

2. **Set up the Database Schema**
   - Navigate to the SQL Editor in your Supabase dashboard
   - Run the SQL queries from the `project-plan.md` file to create the necessary tables and views

## Running the Application

### Using Docker (Recommended)

```bash
docker compose up --build
```
Access the application at http://localhost:8501

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r app/requirements.txt
   ```

2. **Run the Streamlit app**
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Validation Criteria

The Stage 1 implementation can be validated by:

1. The Streamlit app runs successfully
2. The app connects to Supabase without errors
3. Test queries return expected results
4. Basic data visualization works

## Troubleshooting

If you encounter connection issues:

1. Verify your Supabase credentials in the `.env` file
2. Ensure your Supabase project is active
3. Check network connectivity
4. Look at the application logs for detailed error messages