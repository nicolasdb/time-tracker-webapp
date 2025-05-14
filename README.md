# Time Tracker Journey

A FastAPI-based web application for tracking time using NFC/RFID tags, providing insights, and managing your productivity journey.

## Features

- **NFC/RFID Tag Tracking**: Track time using physical NFC tags
- **Tag Management**: Create, edit, and delete tags for different projects
- **RFID Event Management**: View and manage RFID events
- **Dashboard**: Visualize your time usage and productivity
- **Reflections**: Daily and weekly reflections on your work and productivity
- **Integration**: Connects with Journey Service for cognitive wealth insights

## Tech Stack

- **Backend**: FastAPI with Jinja2 templates
- **Frontend**: HTMX, Alpine.js, Tailwind CSS with Windster dashboard template
- **Database**: Supabase
- **Integration**: Journey Service API

## Development Setup

### Prerequisites

- Docker and docker-compose
- Supabase account (for database)

### Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/time-tracker-webapp.git
   cd time-tracker-webapp
   ```

2. Create a `.env` file from the example:
   ```
   cp app/.env.example app/.env
   ```
   
3. Update the `.env` file with your Supabase credentials

4. Start the development server:
   ```
   docker-compose up
   ```

5. Access the application at http://localhost:8000

For more detailed information about the Docker setup, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

## Improved Docker Configuration

The application uses an improved Docker configuration that:

- Pulls the Windster dashboard template during build (no need to commit it)
- Uses bind mounts for efficient development
- Automatically builds Tailwind CSS
- Includes health checks for monitoring

## Project Structure

```
app/
├── static/              # Static assets
│   ├── css/             # Compiled CSS
│   ├── js/              # JavaScript files
│   ├── images/          # Images
│   └── src/             # Source files for Tailwind
├── templates/           # Jinja2 templates
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # Dashboard pages
│   ├── tags/            # Tag management pages
│   └── rfid_events/     # RFID event pages
├── routers/             # FastAPI routers
├── models/              # Pydantic models
├── services/            # Business logic
│   └── supabase.py      # Supabase authentication service
├── main.py              # Main application entry
└── requirements.txt     # Python dependencies
```

## Project Roadmap

The project is organized into four levels of development:

### Level 1: Foundation ✅
- ✅ FastAPI + HTMX + Tailwind CSS environment with Docker
- ✅ User authentication system with Supabase
- ✅ Basic navigation structure
- ✅ Project skeleton connected to Supabase

### Level 2: Data Flow (In Progress)
- 🔄 Tag management CRUD operations
- ⏳ RFID event tracking and manual adjustment (Next up!)
- ⏳ Webhook integration for NFC device events
- ⏳ Data persistence in Supabase

### Level 3: Visualization (Upcoming)
- Time tracking dashboard with daily/weekly views
- Project breakdown charts
- Focus session metrics
- Responsive design

### Level 4: Integration (Upcoming)
- Reflection system integration
- Complete data synchronization
- Cognitive Wealth metrics
- End-to-end user flow optimization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
