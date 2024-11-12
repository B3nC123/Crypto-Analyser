import asyncio
import logging
from api.main import app
import uvicorn
from multiprocessing import Process
import streamlit.cli as stcli
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_api():
    """Run the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_frontend():
    """Run the Streamlit frontend."""
    sys.argv = ["streamlit", "run", "src/frontend/dashboard.py"]
    sys.exit(stcli.main())

def main():
    """Main entry point for the application."""
    try:
        # Start API server in a separate process
        api_process = Process(target=run_api)
        api_process.start()
        logger.info("API server started on http://localhost:8000")

        # Start Streamlit frontend
        frontend_process = Process(target=run_frontend)
        frontend_process.start()
        logger.info("Streamlit frontend started")

        # Wait for processes to complete
        api_process.join()
        frontend_process.join()

    except KeyboardInterrupt:
        logger.info("Shutting down application...")
        api_process.terminate()
        frontend_process.terminate()
        api_process.join()
        frontend_process.join()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
