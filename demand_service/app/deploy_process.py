import requests
import os

def deploy_process():
    """Deploy the BPMN process to Camunda"""
    base_url = os.environ.get('CAMUNDA_URL', 'http://localhost:8080')
    url = f"{base_url}/engine-rest/deployment/create"
    
    # Read the BPMN file
    with open('app/processes/demand_confirmation.bpmn', 'rb') as f:
        bpmn_content = f.read()
    
    # Create multipart form data
    files = {
        'file': ('demand_confirmation.bpmn', bpmn_content, 'application/xml')
    }
    
    data = {
        'deployment-name': 'demand-service',
        'enable-duplicate-filtering': 'true'
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code != 200:
        print(f"Failed to deploy process: {response.text}")
        return False
    
    print("Process deployed successfully")
    return True

if __name__ == '__main__':
    deploy_process() 