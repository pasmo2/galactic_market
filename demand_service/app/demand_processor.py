import logging
import threading
import time
from .kafka_client import KafkaClient
from .camunda_client import CamundaClient

logger = logging.getLogger(__name__)

class DemandProcessor:
    """
    Service that consumes demand events from Kafka and processes them with Camunda
    """
    def __init__(self):
        self.kafka_client = KafkaClient()
        self.camunda_client = CamundaClient()
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the demand processor service"""
        if self.running:
            logger.warning("Demand processor is already running")
            return
            
        self.running = True
        logger.info("Starting Demand Processor service")
        
        # Start consuming from Kafka
        self.kafka_client.consume_demand_requests(self.process_demand_request)
        
        logger.info("Demand Processor service started")
        
    def process_demand_request(self, demand_data):
        """Process a demand request from Kafka"""
        try:
            logger.info(f"Processing demand request: {demand_data}")
            
            demand_id = demand_data.get('demand_id')
            user_id = demand_data.get('user_id')
            galactic_object_id = demand_data.get('galactic_object_id')
            price_eur = demand_data.get('price_eur')
            
            if not all([demand_id, user_id, galactic_object_id, price_eur]):
                logger.error(f"Invalid demand data: {demand_data}")
                self.kafka_client.publish_demand_status(
                    demand_id or 'unknown', 
                    "error",
                    {"message": "Invalid demand data"}
                )
                return
                
            # Start Camunda process
            try:
                process_instance = self.camunda_client.start_demand_process(
                    demand_id=demand_id,
                    user_id=user_id,
                    object_id=galactic_object_id,
                    price=price_eur
                )
                
                # Publish success status back to Kafka
                self.kafka_client.publish_demand_status(
                    demand_id, 
                    "process_started",
                    {
                        "process_instance_id": process_instance.get('id'),
                        "message": "Camunda process started successfully"
                    }
                )
                
                logger.info(f"Successfully started Camunda process for demand {demand_id}")
                
            except Exception as e:
                logger.error(f"Failed to start Camunda process: {str(e)}")
                self.kafka_client.publish_demand_status(
                    demand_id, 
                    "error",
                    {"message": f"Failed to start Camunda process: {str(e)}"}
                )
                
        except Exception as e:
            logger.error(f"Error processing demand request: {str(e)}")
            
# Singleton instance
demand_processor = DemandProcessor() 