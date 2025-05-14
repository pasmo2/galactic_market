import requests
import time
import json
import os
from typing import Dict, Any
from .kafka_client import KafkaClient

class CamundaTaskWorker:
    def __init__(self):
        self.base_url = os.environ.get('CAMUNDA_URL', 'http://localhost:8080')
        self.worker_id = "demand_service_worker"
        self.max_tasks = 1
        self.use_priority = True
        self.async_response_timeout = 30000
        self.lock_duration = 10000

    def fetch_and_lock(self, topic: str) -> list:
        """Fetch and lock tasks for a specific topic"""
        url = f"{self.base_url}/engine-rest/external-task/fetchAndLock"
        payload = {
            "workerId": self.worker_id,
            "maxTasks": self.max_tasks,
            "usePriority": self.use_priority,
            "asyncResponseTimeout": self.async_response_timeout,
            "topics": [
                {
                    "topicName": topic,
                    "lockDuration": self.lock_duration
                }
            ]
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching tasks: {response.text}")
            return []

    def complete_task(self, task_id: str, variables: Dict[str, Any] = None) -> bool:
        """Complete a task with optional variables"""
        url = f"{self.base_url}/engine-rest/external-task/{task_id}/complete"
        payload = {
            "workerId": self.worker_id,
            "variables": {}
        }

        if variables:
            for key, value in variables.items():
                payload["variables"][key] = {"value": value}

        response = requests.post(url, json=payload)
        return response.status_code == 204

    def handle_failure(self, task_id: str, error_message: str, error_details: str) -> bool:
        """Handle task failure"""
        url = f"{self.base_url}/engine-rest/external-task/{task_id}/failure"
        payload = {
            "workerId": self.worker_id,
            "errorMessage": error_message,
            "errorDetails": error_details,
            "retries": 0
        }

        response = requests.post(url, json=payload)
        return response.status_code == 204

kafka_client = KafkaClient()

def validate_demand_worker():
    """Worker that handles validate_demand tasks"""
    worker = CamundaTaskWorker()
    
    while True:
        tasks = worker.fetch_and_lock("validate_demand")
        
        for task in tasks:
            try:
                # Extract variables
                variables = task.get('variables', {})
                demand_id = variables.get('demandId', {}).get('value')
                user_id = variables.get('userId', {}).get('value')
                object_id = variables.get('objectId', {}).get('value')
                price = variables.get('price', {}).get('value')
                
                print(f"Validating demand: {demand_id}")
                print(f"User ID: {user_id}")
                print(f"Object ID: {object_id}")
                print(f"Price: {price}")
                
                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "validating_demand",
                    {
                        "user_id": user_id,
                        "object_id": object_id,
                        "price": price
                    }
                )
                
                # In a real scenario, you would validate the demand here
                is_valid = True
                
                # Complete the task
                result = worker.complete_task(task['id'], {"isValid": is_valid})
                
                if result:
                    print(f"Task {task['id']} completed successfully")
                    
                    # Publish completion status to Kafka
                    kafka_client.publish_demand_status(
                        demand_id,
                        "demand_validated",
                        {
                            "is_valid": is_valid
                        }
                    )
                else:
                    print(f"Failed to complete task {task['id']}")
                    
                    # Publish error status to Kafka
                    kafka_client.publish_demand_status(
                        demand_id,
                        "validation_error",
                        {
                            "task_id": task['id'],
                            "message": "Failed to complete task"
                        }
                    )
            except Exception as e:
                print(f"Error processing task: {str(e)}")
                
        time.sleep(5)  # Poll every 5 seconds

def check_object_availability_worker():
    worker = CamundaTaskWorker()
    while True:
        tasks = worker.fetch_and_lock("check_object_availability")
        for task in tasks:
            try:
                # Get variables
                object_id = task["variables"]["objectId"]["value"]
                demand_id = task["variables"]["demandId"]["value"]

                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "checking_object",
                    {
                        "object_id": object_id
                    }
                )

                # Check object availability (for now, just log the values)
                print(f"Checking availability of object: {object_id}")

                # Complete task
                worker.complete_task(task["id"], {"isAvailable": True})
                
                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "object_available",
                    {
                        "object_id": object_id,
                        "is_available": True
                    }
                )
            except Exception as e:
                worker.handle_failure(task["id"], str(e), str(e))
        time.sleep(1)

def check_user_balance_worker():
    worker = CamundaTaskWorker()
    while True:
        tasks = worker.fetch_and_lock("check_user_balance")
        for task in tasks:
            try:
                # Get variables
                user_id = task["variables"]["userId"]["value"]
                price = task["variables"]["price"]["value"]
                demand_id = task["variables"]["demandId"]["value"]

                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "checking_balance",
                    {
                        "user_id": user_id,
                        "price": price
                    }
                )

                # Check user balance (for now, just log the values)
                print(f"Checking balance for user: {user_id}")
                print(f"Required balance: {price}")

                # Complete task
                worker.complete_task(task["id"], {"hasBalance": True})
                
                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "balance_sufficient",
                    {
                        "user_id": user_id,
                        "price": price,
                        "has_balance": True
                    }
                )
            except Exception as e:
                worker.handle_failure(task["id"], str(e), str(e))
        time.sleep(1)

def update_ownership_worker():
    worker = CamundaTaskWorker()
    while True:
        tasks = worker.fetch_and_lock("update_ownership")
        for task in tasks:
            try:
                # Get variables
                user_id = task["variables"]["userId"]["value"]
                object_id = task["variables"]["objectId"]["value"]
                demand_id = task["variables"]["demandId"]["value"]
                
                # Get process instance ID
                process_instance_id = task.get("processInstanceId")

                # Publish status update to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "updating_ownership",
                    {
                        "user_id": user_id,
                        "object_id": object_id,
                        "process_instance_id": process_instance_id
                    }
                )

                # Update ownership (for now, just log the values)
                print(f"Updating ownership of object: {object_id}")
                print(f"New owner: {user_id}")

                # Complete task
                worker.complete_task(task["id"], {"ownershipUpdated": True})
                
                # Publish ownership updated status to Kafka
                kafka_client.publish_demand_status(
                    demand_id,
                    "ownership_updated",
                    {
                        "user_id": user_id,
                        "object_id": object_id,
                        "success": True
                    }
                )
                
                # Since this is the final step in the process, also publish a process_completed event
                kafka_client.publish_demand_status(
                    demand_id,
                    "process_completed",
                    {
                        "message": "Process completed successfully",
                        "process_instance_id": process_instance_id,
                        "user_id": user_id,
                        "object_id": object_id
                    }
                )
                
                print(f"Process completed for demand: {demand_id}")
            except Exception as e:
                worker.handle_failure(task["id"], str(e), str(e))
                
                # Publish error status to Kafka (if we have the demand ID)
                demand_id = task["variables"].get("demandId", {}).get("value")
                if demand_id:
                    kafka_client.publish_demand_status(
                        demand_id,
                        "error",
                        {
                            "message": f"Error updating ownership: {str(e)}"
                        }
                    )
        time.sleep(1) 