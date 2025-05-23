# Galactic Market

A microservices-based application for trading galactic objects in the universe.

## Architecture

The application consists of the following microservices:

1. **API Gateway** (`http://localhost:8000`) - Entry point for all client requests
2. **User Service** (`http://localhost:5001`) - Handles user management and authentication
3. **Object Service** (`http://localhost:5002`) - Manages galactic objects and their properties 
4. **Demand Service** (`http://localhost:5003`) - Handles trading and purchase requests
5. **Database** - Shared PostgreSQL database for all services

## API Gateway

The API Gateway provides a unified entry point for all client requests. It routes requests to the appropriate microservice and provides additional features like:

- **Routing**: Requests are forwarded to the correct service based on the URL path
- **Service Discovery**: The gateway knows the locations of all microservices
- **Health Checks**: Monitors the health of all microservices
- **Error Handling**: Provides unified error responses

## Getting Started

To run the application:

```bash
# Build and start all services
docker-compose up

# Access the services
API Gateway: http://localhost:8000
User Service: http://localhost:5001
Object Service: http://localhost:5002
Demand Service: http://localhost:5003
```

## how to run the kafka+camunda part:
### get our docker setup running
docker-compose up --build
### start our camunda worker
docker-compose exec demand_service python -m app.start_workers
### start our kafka message viewer
python kafka_message_viewer.py
#### create a demand to fire the camunda process
curl -X POST -H "Content-Type: application/json" -d '{"user_id": "99c4735c-8a55-4a74-980f-b5e2c34494bd", "galactic_object_id": "973363d7-9799-45a4-9a77-e9b7adbdc6d5", "price_eur": 7000}' http://localhost:8000/demands


observe!