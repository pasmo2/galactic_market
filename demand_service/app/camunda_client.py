import requests
import os
import json
from typing import Dict, Any

class CamundaClient:
    def __init__(self):
        self.base_url = os.environ.get('CAMUNDA_URL', 'http://localhost:8080')
        self.process_key = 'galactic_market_demand'

    def start_demand_process(self, demand_id: str, user_id: str, object_id: str, price: float) -> Dict[str, Any]:
        """Start a new demand confirmation process"""
        url = f"{self.base_url}/engine-rest/process-definition/key/{self.process_key}/start"
        
        variables = {
            "demandId": {"value": demand_id, "type": "String"},
            "userId": {"value": user_id, "type": "String"},
            "objectId": {"value": object_id, "type": "String"},
            "price": {"value": price, "type": "Double"}
        }

        response = requests.post(
            url,
            json={"variables": variables},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to start process: {response.text}")
        
        return response.json()

    def complete_task(self, task_id: str, variables: Dict[str, Any] = None) -> None:
        """Complete a user task"""
        url = f"{self.base_url}/engine-rest/task/{task_id}/complete"
        
        payload = {"variables": variables} if variables else {}
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 204:
            raise Exception(f"Failed to complete task: {response.text}")

    def get_user_tasks(self, user_id: str) -> list:
        """Get all tasks assigned to a user"""
        url = f"{self.base_url}/engine-rest/task"
        
        response = requests.get(
            url,
            params={"assignee": user_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get tasks: {response.text}")
        
        return response.json()

    def claim_task(self, task_id: str, user_id: str) -> None:
        """Claim a task for a user"""
        url = f"{self.base_url}/engine-rest/task/{task_id}/claim"
        
        response = requests.post(
            url,
            json={"userId": user_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 204:
            raise Exception(f"Failed to claim task: {response.text}") 