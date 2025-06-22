import requests
import json
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime

class N8nAPIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize n8n API client"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if api_key:
            self.headers['X-N8N-API-KEY'] = api_key
        
        print(f"✅ N8N API Client initialized for: {self.base_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to n8n"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers, timeout=10)
            if response.status_code == 200:
                return {"status": "success", "message": "Connected to n8n successfully"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Cannot connect to n8n. Is it running?"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_workflows(self) -> Dict[str, Any]:
        """Get all workflows from n8n"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/workflows", headers=self.headers)
            if response.status_code == 200:
                return {"status": "success", "workflows": response.json()}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow in n8n"""
        try:
            print(f"🚀 Creating workflow: {workflow_data.get('name')}")
            response = requests.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self.headers,
                json=workflow_data
            )
            
            print(f"📡 API Response: {response.status_code}")
            
            # n8n can return either 200 or 201 for successful creation
            if response.status_code in [200, 201]:
                created_workflow = response.json()
                workflow_id = created_workflow.get("id")
                print(f"✅ Workflow created with ID: {workflow_id}")
                return {
                    "status": "success",
                    "id": workflow_id,
                    "message": f"Workflow '{workflow_data.get('name')}' created successfully"
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Creation failed: {error_msg}")
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Exception during creation: {error_msg}")
            return {"status": "error", "message": error_msg}
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing workflow"""
        try:
            response = requests.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=workflow_data
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": "Workflow updated successfully"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate a workflow"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {"status": "success", "message": "Workflow activated"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_workflow(self, workflow_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow manually"""
        try:
            payload = {"workflowData": data} if data else {}
            response = requests.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 201:
                return {"status": "success", "execution": response.json()}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_workflow_with_debug(self, workflow_data):
        """Enhanced create_workflow method with JSON logging"""
    
    # Create debug directory
        debug_dir = "n8n_deployment_debug"
        os.makedirs(debug_dir, exist_ok=True)
    
    # Get workflow name
        workflow_name = workflow_data.get('name', 'Unknown_Workflow')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Log the JSON being sent to n8n
        json_file = os.path.join(debug_dir, f"SENDING_{workflow_name.replace(' ', '_')}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
        print(f"\n🔍 N8N API DEBUG:")
        print(f"📤 Sending JSON: {json_file}")
        print(f"📊 Workflow: {workflow_name}")
        print(f"🔢 Nodes: {len(workflow_data.get('nodes', []))}")
        print(f"🔗 Connections: {len(workflow_data.get('connections', {}))}")
    
    # Show preview of what's being sent
        json_str = json.dumps(workflow_data, indent=2)
        print(f"\n📋 SENDING TO N8N (preview):")
        print("-" * 50)
        print(json_str[:800])
        if len(json_str) > 800:
            print("... (truncated, see full JSON in log file)")
        print("-" * 50)
    
    # Make the actual API call (your existing logic)
        try:
            import requests
            url = f"{self.base_url}/api/v1/workflows"
            response = requests.post(url, headers=self.headers, json=workflow_data)
            
            # Log the response
            response_file = os.path.join(debug_dir, f"RESPONSE_{workflow_name.replace(' ', '_')}_{timestamp}.json")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ SUCCESS! Response: {response_file}")
                print(f"🆔 Workflow ID: {response_data.get('id')}")
                
                return {
                    'status': 'success',
                    'id': response_data.get('id'),
                    'message': f"Workflow '{workflow_name}' created successfully"
                }
            else:
                error_data = {"status_code": response.status_code, "error": response.text}
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(error_data, f, indent=2, ensure_ascii=False)
                
                print(f"❌ FAILED! Error response: {response_file}")
                print(f"Status: {response.status_code}")
                print(f"Error: {response.text[:200]}...")
                
                return {
                    'status': 'error',
                    'message': f"Failed: {response.status_code} - {response.text}",
                    'status_code': response.status_code
                }
            
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            return {'status': 'error', 'message': str(e)}


# Test the connection
if __name__ == "__main__":
    from config import Config
    
    client = N8nAPIClient(Config.N8N_BASE_URL, Config.N8N_API_KEY)
    result = client.test_connection()
    print(f"Connection test: {result}")