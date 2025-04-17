# Galactic Market API Gateway

This API Gateway serves as a unified entry point for all microservices in the Galactic Market application.

## Features

- **Unified API Endpoint**: All client requests go through a single host/port
- **Routing**: Automatically routes requests to the appropriate microservice
- **Service Discovery**: Knows the location of all microservices
- **Health Checks**: Monitors the health of all microservices
- **Logging**: Provides centralized request logging

## API Endpoints

### User Service
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `POST /api/login` - User login

### Galactic Object Service
- `GET /api/galactic_objects` - Get all galactic objects
- `GET /api/galactic_objects_search` - Search for galactic objects by name
- `POST /api/add_galactic_objects` - Add a new galactic object
- `DELETE /api/galactic_objects/{uuid}` - Delete a galactic object
- `GET /api/galactic_objects/owned_by/{user_id}` - Get objects owned by a user

### Demand Service
- `GET /api/demands` - Get all demands (optionally filtered by user_id)
- `POST /api/demands` - Create a new demand
- `POST /api/demands/{uuid}/confirm` - Confirm a demand (transfer ownership)
- `DELETE /api/demands/{uuid}` - Delete a demand

### System
- `GET /api/health` - Check the health of all services

## Development

To run the API Gateway in development mode:

```bash
export GATEWAY_ENV=development
python app/app.py
```

## Production

In production, the API Gateway will communicate with the microservices using their Docker service names. 