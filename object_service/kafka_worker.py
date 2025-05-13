#!/usr/bin/env python
"""
Standalone script to run the Kafka consumer for the object service.
This allows running the consumer independently from the API service.
"""
import os
import sys
import time
import signal
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the consumer
from app.demand_consumer import run_consumer

if __name__ == "__main__":
    logger.info("Starting Kafka consumer worker...")
    
    # Run the consumer
    thread, consumer = run_consumer()
    
    # Register signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Stopping worker...")
        consumer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Kafka consumer worker is running. Press CTRL+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        consumer.stop()
        thread.join(timeout=5)
        logger.info("Worker stopped") 