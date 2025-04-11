#!/usr/bin/env python3
"""
Helper script to start the webhook server.
This script correctly runs the webhook server module and handles environment variables.
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_server():
    """Start the webhook server using the appropriate command."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Command to start the webhook server
    cmd = [sys.executable, "-m", "app.webhook_server"]
    
    try:
        logger.info("Starting webhook server...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Set the working directory to the project root
        os.chdir(script_dir)
        
        # Start the server process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        logger.info("Webhook server started.")
        logger.info("Press Ctrl+C to stop the server.")
        
        # Stream the output from the server process
        for line in process.stdout:
            print(line, end='')
            
        # Wait for the process to complete
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"Webhook server exited with code {process.returncode}")
            return False
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected. Stopping the server...")
        return True
        
    except Exception as e:
        logger.error(f"Error starting webhook server: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== Time Tracker Webhook Server =====\n")
    print("This script starts the webhook server for Time Tracker")
    print("The server will listen for events from NFC reader devices")
    print("Access the server at: http://localhost:8000/api/health\n")
    
    try:
        # Start the server
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    
    print("\nTroubleshooting:")
    print("1. Make sure required environment variables are set (SUPABASE_URL, SUPABASE_KEY, etc.)")
    print("2. Check if port 8000 is already in use by another application")
    print("3. Verify that all required Python packages are installed:")
    print("   pip install -r app/requirements.txt\n")