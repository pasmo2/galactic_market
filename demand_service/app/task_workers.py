import requests
import time
import json
import os
from typing import Dict, Any

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

def validate_demand_worker():
    worker = CamundaTaskWorker()
    while True:
        tasks = worker.fetch_and_lock("validate_demand")
        for task in tasks:
            try:
                # Get variables
                demand_id = task["variables"]["demandId"]["value"]
                user_id = task["variables"]["userId"]["value"]
                object_id = task["variables"]["objectId"]["value"]
                price = task["variables"]["price"]["value"]

                # Validate demand (for now, just log the values)
                print(f"Validating demand: {demand_id}")
                print(f"User ID: {user_id}")
                print(f"Object ID: {object_id}")
                print(f"Price: {price}")

                # Complete task
                worker.complete_task(task["id"], {"isValid": True})
            except Exception as e:
                worker.handle_failure(task["id"], str(e), str(e))
        time.sleep(1)

def check_object_availability_worker():
    worker = CamundaTaskWorker()
    while True:
        tasks = worker.fetch_and_lock("check_object_availability")
        for task in tasks:
            try:
                # Get variables
                object_id = task["variables"]["objectId"]["value"]

                # Check object availability (for now, just log the values)
                print(f"Checking availability of object: {object_id}")

                # Complete task
                worker.complete_task(task["id"], {"isAvailable": True})
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

                # Check user balance (for now, just log the values)
                print(f"Checking balance for user: {user_id}")
                print(f"Required balance: {price}")

                # Complete task
                worker.complete_task(task["id"], {"hasBalance": True})
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

                # Update ownership (for now, just log the values)
                print(f"Updating ownership of object: {object_id}")
                print(f"New owner: {user_id}")

                # Complete task
                worker.complete_task(task["id"], {"ownershipUpdated": True})
            except Exception as e:
                worker.handle_failure(task["id"], str(e), str(e))
        time.sleep(1) 