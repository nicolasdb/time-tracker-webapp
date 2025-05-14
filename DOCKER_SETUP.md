# Time Tracker Journey: Development Guide

## Improved Docker Setup

The Time Tracker Journey application has been set up with an improved Docker configuration to simplify development and deployment. Here's what you need to know:

### Key Features

1. **Bind Mounts**: The application uses bind mounts to reflect changes in your code immediately without having to rebuild the container. This makes development much faster.

2. **Windster Template**: The Windster dashboard template is now pulled directly during the Docker build process, so you don't have to commit it to your repository.

3. **Automatic CSS Building**: Tailwind CSS is automatically built during the Docker build process, ensuring your CSS is always up to date.

4. **Health Checks**: The Docker container includes health checks to make sure the service is running properly.

### Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/time-tracker-webapp.git
   cd time-tracker-webapp
   ```

2. **Create a `.env` file**:
   ```bash
   cp app/.env.example app/.env
   # Edit app/.env with your Supabase credentials
   ```

3. **Start the Docker container**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   Open your browser and go to http://localhost:8000

### Development Workflow

1. **Edit files**: Make changes to your code as needed. The changes will be reflected immediately thanks to the bind mount and the hot reload feature.

2. **Stop the container**: When you're done, stop the container:
   ```bash
   docker-compose down
   ```

3. **View logs**: If you need to see the logs, use:
   ```bash
   docker-compose logs -f
   ```

### Troubleshooting

1. **CSS not updating**: If your CSS changes are not reflecting, you may need to rebuild it:
   ```bash
   docker exec time-tracker-webapp npx tailwindcss -i ./static/src/main.css -o ./static/css/main.css
   ```

2. **Container not starting**: Check the logs for error messages:
   ```bash
   docker-compose logs
   ```

3. **API errors**: Make sure your Supabase credentials are correctly set in the `.env` file.

### Next Steps

Now that you have a working foundation (Level 1 completed), you can proceed to Level 2 to implement the Data Flow functionality. This includes setting up tag management, RFID event tracking, and webhook integration.

Remember to commit your changes regularly to keep track of your progress!
