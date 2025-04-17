from flask import Flask, request, jsonify, Response
import requests
import os
from flask_cors import CORS
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Service URLs from environment variables
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user_service:5000')
OBJECT_SERVICE_URL = os.environ.get('OBJECT_SERVICE_URL', 'http://object_service:5000')
DEMAND_SERVICE_URL = os.environ.get('DEMAND_SERVICE_URL', 'http://demand_service:5000')

# For development when running outside Docker
if os.environ.get('GATEWAY_ENV') == 'development':
    USER_SERVICE_URL = 'http://localhost:5001'
    OBJECT_SERVICE_URL = 'http://localhost:5002'
    DEMAND_SERVICE_URL = 'http://localhost:5003'

def forward_request(service_url, path='', **kwargs):
    """
    Forward the request to a microservice and return the response
    """
    url = f"{service_url}/{path}"
    try:
        # Forward the request method, headers, and body
        method = request.method
        headers = {key: value for key, value in request.headers
                  if key.lower() not in ['host', 'content-length']}
        
        data = request.get_data() if request.data else None
        params = request.args

        # Make the request to the service
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            timeout=5
        )

        # Return the response from the service
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forwarding request to {url}: {str(e)}")
        return jsonify({
            "error": "Service unavailable",
            "message": str(e)
        }), 503

# User Service Routes
@app.route('/api/users', methods=['GET', 'POST'])
def proxy_users():
    return forward_request(USER_SERVICE_URL, 'users')

@app.route('/api/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_user_path(path):
    return forward_request(USER_SERVICE_URL, f'users/{path}')

@app.route('/api/login', methods=['POST'])
def proxy_login():
    return forward_request(USER_SERVICE_URL, 'login')

# Galactic Object Service Routes
@app.route('/api/galactic_objects', methods=['GET', 'POST'])
def proxy_objects():
    return forward_request(OBJECT_SERVICE_URL, 'galactic_objects')

@app.route('/api/galactic_objects/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_object_path(path):
    return forward_request(OBJECT_SERVICE_URL, f'galactic_objects/{path}')

@app.route('/api/galactic_objects_search', methods=['GET'])
def proxy_objects_search():
    return forward_request(OBJECT_SERVICE_URL, 'galactic_objects_search')

@app.route('/api/add_galactic_objects', methods=['POST'])
def proxy_add_objects():
    return forward_request(OBJECT_SERVICE_URL, 'add_galactic_objects')

# Demand Service Routes
@app.route('/api/demands', methods=['GET', 'POST'])
def proxy_demands():
    return forward_request(DEMAND_SERVICE_URL, 'demands')

@app.route('/api/demands/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_demand_path(path):
    return forward_request(DEMAND_SERVICE_URL, f'demands/{path}')

# Health Check Endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    health = {
        "status": "up",
        "services": {}
    }
    
    # Check user service
    try:
        user_response = requests.get(f"{USER_SERVICE_URL}/users", timeout=2)
        health["services"]["user_service"] = "up" if user_response.status_code < 500 else "down"
    except:
        health["services"]["user_service"] = "down"
    
    # Check object service
    try:
        object_response = requests.get(f"{OBJECT_SERVICE_URL}/galactic_objects", timeout=2)
        health["services"]["object_service"] = "up" if object_response.status_code < 500 else "down"
    except:
        health["services"]["object_service"] = "down"
    
    # Check demand service
    try:
        demand_response = requests.get(f"{DEMAND_SERVICE_URL}/demands", timeout=2)
        health["services"]["demand_service"] = "up" if demand_response.status_code < 500 else "down"
    except:
        health["services"]["demand_service"] = "down"
    
    # Overall status is "down" if any service is down
    if "down" in health["services"].values():
        health["status"] = "degraded"
    
    return jsonify(health)

if __name__ == '__main__':
    port = int(os.environ.get('GATEWAY_PORT', 8000))
    app.run(host='0.0.0.0', port=port) 