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

### Installation

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
├── main.py              # Main application entry
└── requirements.txt     # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
