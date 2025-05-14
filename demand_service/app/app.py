from flask import Flask
from flask_migrate import Migrate
from .views import demands_bp
from .models import db
from flask_cors import CORS
import os
import logging
from .demand_processor import demand_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@db/mydatabase?client_encoding=utf8')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(demands_bp)

CORS(app)

@app.before_first_request
def init_services():
    """Initialize services when the application starts"""
    logger.info("Initializing demand processor service")
    demand_processor.start()
    
    # Deploy the Camunda process if needed
    from .deploy_process import deploy_process
    deploy_result = deploy_process()
    logger.info(f"Camunda process deployment: {'Success' if deploy_result else 'Failed'}")
    
    logger.info("Service initialization complete")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)