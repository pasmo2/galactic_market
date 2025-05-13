import os
import json
from confluent_kafka import Producer, Consumer, KafkaError
import logging

logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

def delivery_report(err, msg):
    """Callback function for producer message delivery reports"""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

class KafkaProducer:
    def __init__(self):
        """Initialize Kafka producer"""
        self.producer = Producer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'demand-service-producer'
        })
    
    def publish_event(self, topic, event_type, data):
        """Publish an event to a Kafka topic"""
        try:
            # Create event payload
            event = {
                'event_type': event_type,
                'data': data
            }
            
            # Produce message
            self.producer.produce(
                topic,
                key=data.get('uuid', ''),
                value=json.dumps(event).encode('utf-8'),
                callback=delivery_report
            )
            
            # Flush to ensure message is sent
            self.producer.flush()
            
            logger.info(f"Event {event_type} published to {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event to {topic}: {str(e)}")
            return False
    
    def close(self):
        """Close the producer connection"""
        self.producer.flush()

class KafkaConsumer:
    def __init__(self, topics, group_id, auto_offset_reset='earliest'):
        """Initialize Kafka consumer"""
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset,
            'enable.auto.commit': True
        })
        
        # Subscribe to topics
        if isinstance(topics, str):
            topics = [topics]
        self.consumer.subscribe(topics)
    
    def consume_events(self, timeout=1.0):
        """Consume events from subscribed topics"""
        try:
            msg = self.consumer.poll(timeout)
            
            if msg is None:
                return None
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"Reached end of partition {msg.topic()} [{msg.partition()}]")
                else:
                    logger.error(f"Consumer error: {msg.error()}")
                return None
            
            # Parse message value
            try:
                event = json.loads(msg.value().decode('utf-8'))
                logger.info(f"Received event from {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                return event
            except json.JSONDecodeError:
                logger.error(f"Failed to parse message value: {msg.value()}")
                return None
                
        except Exception as e:
            logger.error(f"Error consuming events: {str(e)}")
            return None
    
    def close(self):
        """Close the consumer connection"""
        self.consumer.close() 