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

## API Endpoints

### User Service
- GET/POST /api/users - Manage users
- POST /api/login - User authentication

### Object Service
- GET/POST /api/galactic_objects - Manage galactic objects
- GET /api/galactic_objects_search - Search for objects
- POST /api/add_galactic_objects - Add new objects
- GET /api/galactic_objects/owned_by/{user_id} - Get user's objects

### Demand Service
- GET/POST /api/demands - Manage demand requests
- POST /api/demands/{uuid}/confirm - Confirm a purchase
- DELETE /api/demands/{uuid} - Delete a demand

### System
- GET /api/health - Check system health 