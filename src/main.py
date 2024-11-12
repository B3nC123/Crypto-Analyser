import asyncio
import logging
import uvicorn
from multiprocessing import Process
import sys
import os
import signal
import subprocess
from src.api.main import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
API_PORT = 8080

# Global process references
api_process = None
frontend_process = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal")
    shutdown()

def shutdown():
    """Shutdown all processes gracefully."""
    global api_process, frontend_process
    
    logger.info("Shutting down application...")
    
    try:
        if api_process:
            logger.info("Stopping API server...")
            api_process.terminate()
            api_process.join(timeout=5)
            
        if frontend_process:
            logger.info("Stopping frontend...")
            frontend_process.terminate()
            frontend_process.join(timeout=5)
            
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    finally:
        logger.info("Application shutdown complete")
        sys.exit(0)

def run_api():
    """Run the FastAPI server."""
    try:
        logger.debug("Starting API server with uvicorn...")
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=API_PORT,
            reload=False,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Error running API server: {e}")
        shutdown()

def run_frontend():
    """Run the Streamlit frontend."""
    try:
        dirname = os.path.dirname(__file__)
        frontend_path = os.path.join(dirname, "frontend", "dashboard.py")
        python_path = sys.executable
        streamlit_script = os.path.join(os.path.dirname(python_path), "Scripts", "streamlit")
        
        if os.name == 'nt':  # Windows
            streamlit_script += '.exe'
        
        if not os.path.exists(streamlit_script):
            # Try LocalCache path for Windows Store Python
            streamlit_script = os.path.join(
                os.path.expanduser("~"),
                "AppData", "Local", "Packages",
                "PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0",
                "LocalCache", "local-packages", "Python312", "Scripts",
                "streamlit.exe"
            )
        
        if not os.path.exists(streamlit_script):
            raise FileNotFoundError(f"Could not find streamlit executable. Tried: {streamlit_script}")
        
        logger.debug(f"Using Python from: {python_path}")
        logger.debug(f"Using Streamlit from: {streamlit_script}")
        logger.debug(f"Running frontend from: {frontend_path}")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(dirname))
        env["API_PORT"] = str(API_PORT)  # Pass API port to frontend
        
        # Run streamlit as a subprocess
        process = subprocess.Popen(
            [python_path, streamlit_script, "run", frontend_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor the process output
        while True:
            output = process.stdout.readline()
            if output:
                logger.debug(f"Streamlit: {output.strip()}")
            error = process.stderr.readline()
            if error:
                logger.error(f"Streamlit Error: {error.strip()}")
            
            # Check if process has terminated
            if process.poll() is not None:
                break
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
            
    except Exception as e:
        logger.error(f"Error running frontend: {e}")
        shutdown()

def main():
    """Main entry point for the application."""
    global api_process, frontend_process
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start API server in a separate process
        logger.info("Starting API server...")
        api_process = Process(target=run_api)
        api_process.start()
        logger.info(f"API server started on http://localhost:{API_PORT}")

        # Give the API server a moment to start up
        logger.debug("Waiting for API server to initialize...")
        asyncio.new_event_loop().run_until_complete(asyncio.sleep(2))

        # Start Streamlit frontend
        logger.info("Starting frontend...")
        frontend_process = Process(target=run_frontend)
        frontend_process.start()
        logger.info("Streamlit frontend started")

        # Wait for processes to complete
        while True:
            if not api_process.is_alive() or not frontend_process.is_alive():
                logger.error("One of the processes has terminated unexpectedly")
                shutdown()
            asyncio.new_event_loop().run_until_complete(asyncio.sleep(1))

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        shutdown()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        shutdown()

if __name__ == "__main__":
    main()
