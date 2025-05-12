import os
import requests
import json
from typing import Dict, Any

class ExternalTaskWorker:
    def __init__(self):
        self.base_url = os.environ.get('CAMUNDA_URL', 'http://localhost:8080')
        self.worker_id = 'demand-service-worker'
        self.topics = [
            'validate_demand',
            'check_object_availability',
            'check_user_balance',
            'update_ownership'
        ]

    def fetch_and_lock_tasks(self) -> list:
        """Fetch and lock external tasks"""
        url = f"{self.base_url}/engine-rest/external-task/fetchAndLock"
        
        payload = {
            "workerId": self.worker_id,
            "maxTasks": 10,
            "topics": [
                {
                    "topicName": topic,
                    "lockDuration": 10000
                } for topic in self.topics
            ]
        }

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            print(f"Failed to fetch tasks: {response.text}")
            return []

        return response.json()

    def complete_task(self, task_id: str, variables: Dict[str, Any] = None) -> None:
        """Complete an external task"""
        url = f"{self.base_url}/engine-rest/external-task/{task_id}/complete"
        
        payload = {
            "workerId": self.worker_id,
            "variables": variables or {}
        }

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 204:
            print(f"Failed to complete task: {response.text}")

    def handle_validate_demand(self, task: Dict[str, Any]) -> None:
        """Handle validate demand task"""
        variables = task.get('variables', {})
        demand_id = variables.get('demandId', {}).get('value')
        user_id = variables.get('userId', {}).get('value')
        object_id = variables.get('objectId', {}).get('value')
        price = variables.get('price', {}).get('value')

        # Validate demand (for now, just log the values)
        print(f"Validating demand: {demand_id}")
        print(f"User ID: {user_id}")
        print(f"Object ID: {object_id}")
        print(f"Price: {price}")

        # Set validation result
        self.complete_task(task['id'], {
            "isValid": {"value": True, "type": "Boolean"}
        })

    def handle_check_object_availability(self, task: Dict[str, Any]) -> None:
        """Handle check object availability task"""
        variables = task.get('variables', {})
        object_id = variables.get('objectId', {}).get('value')

        # Check object availability (for now, just log the value)
        print(f"Checking object availability: {object_id}")

        # Set availability result
        self.complete_task(task['id'], {
            "isAvailable": {"value": True, "type": "Boolean"}
        })

    def handle_check_user_balance(self, task: Dict[str, Any]) -> None:
        """Handle check user balance task"""
        variables = task.get('variables', {})
        user_id = variables.get('userId', {}).get('value')
        price = variables.get('price', {}).get('value')

        # Check user balance (for now, just log the values)
        print(f"Checking user balance: {user_id}")
        print(f"Price: {price}")

        # Set balance check result
        self.complete_task(task['id'], {
            "hasSufficientBalance": {"value": True, "type": "Boolean"}
        })

    def handle_update_ownership(self, task: Dict[str, Any]) -> None:
        """Handle update ownership task"""
        variables = task.get('variables', {})
        user_id = variables.get('userId', {}).get('value')
        object_id = variables.get('objectId', {}).get('value')

        # Update ownership (for now, just log the values)
        print(f"Updating ownership: {object_id} -> {user_id}")

        # Complete the task
        self.complete_task(task['id'])

    def process_tasks(self) -> None:
        """Process all available tasks"""
        tasks = self.fetch_and_lock_tasks()
        
        for task in tasks:
            topic = task.get('topicName')
            
            if topic == 'validate_demand':
                self.handle_validate_demand(task)
            elif topic == 'check_object_availability':
                self.handle_check_object_availability(task)
            elif topic == 'check_user_balance':
                self.handle_check_user_balance(task)
            elif topic == 'update_ownership':
                self.handle_update_ownership(task)

def start_worker():
    """Start the external task worker"""
    worker = ExternalTaskWorker()
    print("Starting external task worker...")
    
    while True:
        try:
            worker.process_tasks()
        except Exception as e:
            print(f"Error processing tasks: {str(e)}")
            continue

if __name__ == '__main__':
    start_worker() 