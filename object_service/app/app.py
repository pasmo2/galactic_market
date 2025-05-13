from flask import Flask
from flask_migrate import Migrate
from .views import galactic_objects_bp
from .models import db
from flask_cors import CORS
from .demand_consumer import run_consumer
import os
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db/mydatabase')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(galactic_objects_bp)

CORS(app)

# Start Kafka consumer in a separate thread
consumer_thread = None
consumer = None

@app.before_first_request
def start_kafka_consumer():
    global consumer_thread, consumer
    logger.info("Starting Kafka consumer...")
    consumer_thread, consumer = run_consumer()
    logger.info("Kafka consumer started")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)