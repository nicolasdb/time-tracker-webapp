# Time Tracker Webapp

A streamlit-based web application for tracking time spent on projects and tasks.

## Purpose

- Track time spent on different projects and tasks
- Visualize time allocation and productivity
- Generate reports on time usage
- Help improve personal and team productivity

## Features

### Implemented
1. **Supabase Integration**: Connection to Supabase database for data storage
2. **Data Visualization**: Display and visualize time tracking data
3. **Dashboard**: Interactive UI with live metrics and quick navigation
4. **Tag Management**: CRUD operations for RFID tags with project/task assignments
5. **Device Management**: CRUD operations for NFC reader devices
6. **Time Tracking**: View time blocks and raw RFID events by day
7. **Reflection Triggers**: Designate tags that trigger reflections

### Planned
1. **Webhook Service**: Receive and process device events
2. **User Authentication**: Secure login and user-specific data
3. **Advanced Reporting**: Detailed visual charts and reports of time allocation
4. **Export**: Export data in various formats (CSV, PDF)

## Current Status
✅ Stage 1: Foundation - Basic Streamlit + Supabase integration
✅ Stage 2: Data Management Interface - Tag and device management, time tracking
🔄 Stage 3: Webhook Implementation & Authentication - In planning

## Contributing

Interested in contributing? Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start

1. Clone the repository
2. Set up environment variables (see [SETUP.md](SETUP.md))
3. Run the application:

   ```bash
   docker compose up --build
   ```

4. Access the application at `http://localhost:8501`

## Documentation

- [SETUP.md](SETUP.md) - Detailed deployment and configuration guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development and contribution guidelines
- [TECHNICAL.md](TECHNICAL.md) - Technical architecture and implementation details

## License

> Copyright 2025 Nicolas de Barquin
>
> This project is licensed under the Apache License 2.0. See the LICENSE file for details.

Please note that this project uses Docker and Streamlit, which are licensed under their respective licenses.