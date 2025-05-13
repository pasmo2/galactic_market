import os
import time
import signal
import logging
from .kafka_utils import KafkaConsumer
import json
import requests
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import GalacticObject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEMAND_EVENTS_TOPIC = 'demand-events'
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@db/mydatabase')

# Set up the database connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class DemandEventConsumer:
    def __init__(self):
        """Initialize the demand event consumer"""
        self.running = False
        self.consumer = KafkaConsumer(
            topics=DEMAND_EVENTS_TOPIC,
            group_id='object-service-consumer-group'
        )

    def start(self):
        """Start the consumer"""
        self.running = True
        logger.info("Starting demand event consumer...")
        
        while self.running:
            try:
                # Poll for new messages
                event = self.consumer.consume_events(timeout=1.0)
                
                if event:
                    # Process the event
                    self.process_event(event)
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error processing events: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        self.consumer.close()
        logger.info("Demand event consumer stopped")
    
    def process_event(self, event):
        """Process a demand event"""
        event_type = event.get('event_type')
        data = event.get('data', {})
        
        if not event_type or not data:
            logger.warning(f"Invalid event structure: {event}")
            return
        
        logger.info(f"Processing {event_type} event: {data}")
        
        # Process based on event type
        if event_type == 'demand_created':
            self.handle_demand_created(data)
        elif event_type == 'demand_confirmed':
            self.handle_demand_confirmed(data)
        elif event_type == 'demand_deleted':
            self.handle_demand_deleted(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def handle_demand_created(self, data):
        """Handle demand created event"""
        object_id = data.get('galactic_object_id')
        user_id = data.get('user_id')
        
        if not object_id:
            logger.error("Missing galactic_object_id in demand_created event")
            return
        
        # Check object availability
        session = Session()
        try:
            galactic_object = session.query(GalacticObject).filter_by(uuid=object_id).first()
            
            if not galactic_object:
                logger.error(f"Galactic object not found: {object_id}")
                return
            
            logger.info(f"Object {object_id} is available: {not galactic_object.is_sold}")
            
            # For now, just log the information
            logger.info(f"Received demand for object {object_id} from user {user_id}")
        finally:
            session.close()
    
    def handle_demand_confirmed(self, data):
        """Handle demand confirmed event"""
        object_id = data.get('galactic_object_id')
        user_id = data.get('user_id')
        
        if not object_id or not user_id:
            logger.error("Missing required fields in demand_confirmed event")
            return
        
        # Update object ownership
        session = Session()
        try:
            galactic_object = session.query(GalacticObject).filter_by(uuid=object_id).first()
            
            if not galactic_object:
                logger.error(f"Galactic object not found: {object_id}")
                return
            
            # Update ownership
            galactic_object.owner_id = user_id
            galactic_object.is_sold = True
            session.commit()
            
            logger.info(f"Object {object_id} ownership transferred to user {user_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating object ownership: {str(e)}")
        finally:
            session.close()
    
    def handle_demand_deleted(self, data):
        """Handle demand deleted event"""
        object_id = data.get('galactic_object_id')
        
        if not object_id:
            logger.error("Missing galactic_object_id in demand_deleted event")
            return
        
        # Just log the event for now
        logger.info(f"Demand for object {object_id} has been deleted")


def run_consumer():
    """Run the demand event consumer in a separate thread"""
    consumer = DemandEventConsumer()
    
    def signal_handler(sig, frame):
        logger.info("Stopping consumer...")
        consumer.stop()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the consumer
    consumer_thread = threading.Thread(target=consumer.start)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    return consumer_thread, consumer


if __name__ == '__main__':
    # Run the consumer
    thread, consumer = run_consumer()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        consumer.stop()
        thread.join(timeout=5) 