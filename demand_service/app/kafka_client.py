import json
import os
import threading
import time
import uuid
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        self.bootstrap_servers = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.producer = None
        self.consumers = {}
        
        # Topics
        self.DEMAND_REQUESTS_TOPIC = 'demand-requests'
        self.DEMAND_STATUS_TOPIC = 'demand-status-updates'
        
        # Task topics
        self.VALIDATE_DEMAND_TOPIC = 'validate-demand-tasks'
        self.CHECK_OBJECT_TOPIC = 'check-object-availability-tasks'
        self.CHECK_BALANCE_TOPIC = 'check-user-balance-tasks'
        self.UPDATE_OWNERSHIP_TOPIC = 'update-ownership-tasks'
        
        self._init_producer()
        
    def _init_producer(self):
        """Initialize the Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info("Kafka producer initialized")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self.producer = None
            
    def publish_demand_request(self, demand_data):
        """Publish a new demand request to Kafka"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
            
        key = str(uuid.uuid4())
        try:
            future = self.producer.send(
                self.DEMAND_REQUESTS_TOPIC, 
                key=key,
                value=demand_data
            )
            self.producer.flush()
            record_metadata = future.get(timeout=10)
            logger.info(f"Demand request published to {record_metadata.topic} partition {record_metadata.partition}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish demand request: {str(e)}")
            return False
            
    def publish_demand_status(self, demand_id, status, details=None):
        """Publish a status update for a demand"""
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
            
        try:
            message = {
                'demand_id': demand_id,
                'status': status,
                'details': details or {},
                'timestamp': time.time()
            }
            
            future = self.producer.send(
                self.DEMAND_STATUS_TOPIC,
                key=demand_id,
                value=message
            )
            self.producer.flush()
            record_metadata = future.get(timeout=10)
            logger.info(f"Status update published to {record_metadata.topic} partition {record_metadata.partition}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish status update: {str(e)}")
            return False
    
    def consume_demand_requests(self, callback):
        """Start consuming demand requests"""
        consumer_thread = threading.Thread(
            target=self._consume,
            args=(self.DEMAND_REQUESTS_TOPIC, callback),
            daemon=True
        )
        consumer_thread.start()
        self.consumers[self.DEMAND_REQUESTS_TOPIC] = consumer_thread
        
    def _consume(self, topic, callback):
        """Generic consumer method"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=f'demand-service-{topic}',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            logger.info(f"Started consuming from topic: {topic}")
            
            for message in consumer:
                try:
                    logger.info(f"Received message from {topic}: {message.value}")
                    callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error in Kafka consumer for topic {topic}: {str(e)}") 