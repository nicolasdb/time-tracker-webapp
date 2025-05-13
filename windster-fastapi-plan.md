# Windster + FastAPI Integration Plan

## 1. Framework Integration

1. **Structure:**
   - Use FastAPI for backend and routing
   - Adapt Windster HTML templates to Jinja2 format
   - Use Tailwind CSS and Flowbite components from Windster
   - Replace Hugo-specific features with FastAPI equivalents

2. **Dependencies:**
   - FastAPI and Uvicorn for backend
   - Tailwind CSS for styling
   - Flowbite for UI components
   - Alpine.js for client-side interactions

## 2. Directory Structure

```
app/
├── static/              # Static assets
│   ├── css/             # Compiled CSS
│   ├── js/              # JavaScript files
│   ├── images/          # Images
│   └── src/             # Source files for Tailwind
├── templates/           # Jinja2 templates (adapted from Windster)
│   ├── base.html        # Base template (from baseof.html)
│   ├── partials/        # Shared components
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # Dashboard pages
│   ├── tags/            # Tag management pages
│   └── rfid_events/     # RFID event pages
├── routers/             # FastAPI routers
├── models/              # Pydantic models
├── services/            # Business logic
├── main.py              # Main application entry
├── requirements.txt     # Python dependencies
├── package.json         # NPM dependencies
└── tailwind.config.js   # Tailwind configuration
```

## 3. Implementation Steps

1. **Setup Framework:**
   - Install FastAPI and dependencies
   - Configure Jinja2 templates
   - Set up static file serving

2. **Template Adaptation:**
   - Convert Windster templates from Hugo to Jinja2
   - Implement base templates and layouts
   - Adapt partials for reuse

3. **Asset Pipeline:**
   - Configure Tailwind CSS with Flowbite
   - Set up build process for CSS
   - Include necessary JavaScript libraries

4. **Page Implementation:**
   - Authentication pages
   - Dashboard components
   - Tag management CRUD
   - RFID event management

## 4. FastAPI Integration Specifics

1. **Authentication:**
   - Use FastAPI's security utilities
   - Integrate with Supabase auth

2. **API Routes:**
   - Define RESTful endpoints for data
   - Implement HTMX-friendly response formats
   - Create separate routers for different features

3. **Database Access:**
   - Use Supabase client
   - Implement repository pattern for data access
   - Define clear data models

## 5. HTMX Integration

1. **Dynamic Updates:**
   - Use HTMX for partial page updates
   - Implement server-side rendering for components
   - Leverage HTMX triggers for UI interactions

2. **Form Handling:**
   - Use HTMX for form submissions
   - Implement validation feedback
   - Support progressive enhancement

## 6. Next Steps

1. Create base template structure
2. Set up Tailwind CSS build process
3. Implement authentication pages
4. Develop dashboard layout
5. Build tag management CRUD
