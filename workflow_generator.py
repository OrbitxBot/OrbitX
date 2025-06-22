import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import os
from mistralai import Mistral

class EnhancedN8nWorkflowGenerator:
    def __init__(self, mistral_client=None):
        """Initialize the enhanced workflow generator with AI capabilities"""
        self.mistral_client = mistral_client
        self.node_registry = self._initialize_node_registry()
        self.workflow_templates = self._initialize_workflow_templates()
        print("✅ Enhanced N8N Workflow Generator initialized")
    
    def _initialize_node_registry(self) -> Dict[str, Dict]:
        """Registry of all available n8n node types with their configurations"""
        return {
            "webhook": {
                "type": "n8n-nodes-base.webhook",
                "category": "trigger",
                "description": "Receives HTTP requests",
                "default_params": {"httpMethod": "POST", "responseMode": "onReceived"}
            },
            "manual_trigger": {
                "type": "n8n-nodes-base.manualTrigger",
                "category": "trigger",
                "description": "Manual workflow trigger",
                "default_params": {}
            },
            "schedule": {
                "type": "n8n-nodes-base.scheduleTrigger",
                "category": "trigger",
                "description": "Time-based workflow trigger",
                "default_params": {"rule": {"interval": [{"field": "hours", "value": 1}]}}
            },
            "email_send": {
                "type": "n8n-nodes-base.emailSend",
                "category": "action",
                "description": "Send email notifications",
                "default_params": {"fromEmail": "noreply@company.com"}
            },
            "http_request": {
                "type": "n8n-nodes-base.httpRequest",
                "category": "action",
                "description": "Make HTTP API calls",
                "default_params": {"method": "POST", "sendHeaders": True}
            },
            "function": {
                "type": "n8n-nodes-base.function",
                "category": "processing",
                "description": "Execute custom JavaScript code",
                "default_params": {}
            },
            "code": {
                "type": "n8n-nodes-base.code",
                "category": "processing",
                "description": "Execute JavaScript with full access",
                "default_params": {"language": "javascript"}
            },
            "set": {
                "type": "n8n-nodes-base.set",
                "category": "processing",
                "description": "Set or modify data",
                "default_params": {"options": {}}
            },
            "if": {
                "type": "n8n-nodes-base.if",
                "category": "logic",
                "description": "Conditional branching",
                "default_params": {}
            },
            "switch": {
                "type": "n8n-nodes-base.switch",
                "category": "logic",
                "description": "Multi-path routing",
                "default_params": {"fallbackOutput": 1}
            },
            "merge": {
                "type": "n8n-nodes-base.merge",
                "category": "logic",
                "description": "Merge multiple data streams",
                "default_params": {"mode": "append"}
            },
            "hubspot": {
                "type": "n8n-nodes-base.hubspot",
                "category": "crm",
                "description": "HubSpot CRM integration",
                "default_params": {"resource": "contact", "operation": "create"}
            },
            "salesforce": {
                "type": "n8n-nodes-base.salesforce",
                "category": "crm",
                "description": "Salesforce CRM integration",
                "default_params": {"resource": "lead", "operation": "create"}
            },
            "slack": {
                "type": "n8n-nodes-base.slack",
                "category": "communication",
                "description": "Slack messaging",
                "default_params": {"resource": "message", "operation": "post"}
            },
            "google_sheets": {
                "type": "n8n-nodes-base.googleSheets",
                "category": "data",
                "description": "Google Sheets integration",
                "default_params": {"resource": "spreadsheet", "operation": "append"}
            },
            "wait": {
                "type": "n8n-nodes-base.wait",
                "category": "flow",
                "description": "Wait for specified time",
                "default_params": {"unit": "seconds", "amount": 5}
            }
        }
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict]:
        """Initialize workflow pattern templates"""
        return {
            "simple_automation": {
                "pattern": ["trigger", "processing", "action"],
                "description": "Basic automation workflow"
            },
            "approval_workflow": {
                "pattern": ["trigger", "processing", "notification", "logic", "action"],
                "description": "Workflow with approval steps"
            },
            "data_processing": {
                "pattern": ["trigger", "processing", "logic", "action", "notification"],
                "description": "Data processing and routing"
            },
            "crm_integration": {
                "pattern": ["trigger", "processing", "crm", "logic", "notification"],
                "description": "CRM integration workflow"
            },
            "multi_channel": {
                "pattern": ["trigger", "processing", "logic", "action", "communication", "data"],
                "description": "Multi-channel automation"
            }
        }
    
    def generate_workflow_from_description(self, description: str) -> Dict[str, Any]:
        """Generate a complete n8n workflow from natural language description"""
        print(f"🤖 Generating workflow for: {description}")
        
        try:
            # Use AI if available, otherwise use pattern matching
            if self.mistral_client:
                return self._generate_ai_workflow(description)
            else:
                return self._generate_pattern_workflow(description)
        except Exception as e:
            print(f"⚠️ Error in workflow generation: {e}")
            return self._generate_fallback_workflow(description)
    
    def _generate_ai_workflow(self, description: str) -> Dict[str, Any]:
        from mistralai import Mistral
        """Generate workflow using AI"""
        from mistralai.models import ChatMessage
        
        # Create comprehensive AI prompt
        prompt = self._create_ai_prompt(description)
        
        try:
            messages = [
                ChatMessage(role="system", content=self._get_system_prompt()),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.mistral_client.chat(
                model="mistral-large-latest",
                messages=messages,
                temperature=0.3,
                max_tokens=6000
            )
            
            # Parse AI response
            workflow_json_str = response.choices[0].message.content.strip()
            workflow_json = self._parse_ai_response(workflow_json_str)
            
            # Enhance and validate
            workflow_json = self._enhance_workflow(workflow_json, description)
            return workflow_json
            
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            return self._generate_pattern_workflow(description)
    
    def _create_ai_prompt(self, description: str) -> str:
        """Create comprehensive AI prompt for workflow generation"""
        node_types = "\n".join([
            f"- {name}: {info['type']} - {info['description']}"
            for name, info in self.node_registry.items()
        ])
        
        return f"""
Generate a complete n8n workflow JSON for: "{description}"

REQUIREMENTS:
1. Create 4-8 interconnected nodes for a realistic workflow
2. Use appropriate n8n node types from the registry below
3. Include proper node connections and data flow
4. Add realistic parameters for each node
5. Position nodes 200px apart horizontally
6. Return ONLY valid JSON with no explanations

AVAILABLE NODE TYPES:
{node_types}

WORKFLOW STRUCTURE:
{{
    "id": "unique-workflow-id",
    "name": "Workflow Name",
    "active": false,
    "nodes": [
        {{
            "id": "unique-node-id",
            "name": "Node Display Name",
            "type": "n8n-nodes-base.nodetype",
            "position": [x, y],
            "parameters": {{
                // Node-specific parameters
            }},
            "typeVersion": 1
        }}
    ],
    "connections": {{
        "NodeName": {{
            "main": [[{{"node": "NextNodeName", "type": "main", "index": 0}}]]
        }}
    }},
    "settings": {{}},
    "staticData": {{}},
    "tags": [],
    "triggerCount": 1,
    "updatedAt": "{datetime.now().isoformat()}",
    "versionId": "unique-version-id"
}}

EXAMPLES OF GOOD WORKFLOWS:
- Lead Processing: webhook → function(scoring) → switch(route) → crm(create) → email(notify)
- Content Approval: webhook → function(validate) → slack(notify) → wait → switch(approved) → http_request(publish)
- Data Sync: schedule → http_request(fetch) → function(transform) → google_sheets(update) → email(report)

Generate the workflow now:
"""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI"""
        return """You are an expert n8n workflow architect. You create functional, realistic automation workflows.

RULES:
1. Always include proper node IDs and connections
2. Use realistic parameters for each node type
3. Create workflows that solve real business problems
4. Include error handling where appropriate
5. Make workflows that are actually deployable
6. Return only valid JSON - no markdown, no explanations"""
    
    def _generate_pattern_workflow(self, description: str) -> Dict[str, Any]:
        """Generate workflow using pattern matching"""
        print("🔄 Using pattern-based generation")
        
        # Analyze description for keywords
        keywords = self._analyze_description(description)
        
        # Select appropriate workflow pattern
        pattern = self._select_workflow_pattern(keywords)
        
        # Generate nodes based on pattern
        nodes = self._generate_nodes_from_pattern(pattern, keywords, description)
        
        # Create connections
        connections = self._create_connections(nodes)
        
        # Build complete workflow
        return self._build_workflow(description, nodes, connections)
    
    def _analyze_description(self, description: str) -> Dict[str, List[str]]:
        """Analyze description for workflow components"""
        desc_lower = description.lower()
        
        return {
            "triggers": [word for word in ["form", "webhook", "schedule", "manual", "email"] if word in desc_lower],
            "actions": [word for word in ["email", "slack", "api", "database", "crm"] if word in desc_lower],
            "logic": [word for word in ["if", "condition", "approve", "route", "check"] if word in desc_lower],
            "integrations": [word for word in ["hubspot", "salesforce", "sheets", "slack"] if word in desc_lower],
            "data": [word for word in ["process", "transform", "validate", "score"] if word in desc_lower]
        }
    
    def _select_workflow_pattern(self, keywords: Dict[str, List[str]]) -> List[str]:
        """Select workflow pattern based on keywords"""
        if keywords["logic"] and keywords["integrations"]:
            return ["webhook", "function", "switch", "crm", "email"]
        elif keywords["data"] and keywords["actions"]:
            return ["webhook", "function", "http_request", "email"]
        elif "approve" in " ".join(keywords["logic"]):
            return ["webhook", "function", "slack", "wait", "switch", "email"]
        else:
            return ["webhook", "function", "email"]
    
    def _generate_nodes_from_pattern(self, pattern: List[str], keywords: Dict, description: str) -> List[Dict]:
        """Generate nodes based on pattern"""
        nodes = []
        x_position = 240
        
        for i, node_type in enumerate(pattern):
            node_name = self._generate_node_name(node_type, i, keywords)
            node_config = self._generate_node_config(node_type, keywords, description)
            
            node = self._create_node(
                node_type=node_type,
                name=node_name,
                position=[x_position, 300],
                config=node_config
            )
            
            nodes.append(node)
            x_position += 200
        
        return nodes
    
    def _generate_node_name(self, node_type: str, index: int, keywords: Dict) -> str:
        """Generate appropriate node name"""
        name_mappings = {
            "webhook": "Data Input",
            "function": "Process Data",
            "switch": "Route Decision",
            "email": "Send Notification",
            "slack": "Slack Alert",
            "http_request": "API Call",
            "crm": "Update CRM",
            "hubspot": "HubSpot CRM",
            "salesforce": "Salesforce CRM"
        }
        
        return name_mappings.get(node_type, f"Step {index + 1}")
    
    def _generate_node_config(self, node_type: str, keywords: Dict, description: str) -> Dict:
        """Generate node configuration based on context"""
        configs = {
            "webhook": {"path": f"/{description.lower().replace(' ', '-')[:20]}"},
            "function": {"functionCode": self._generate_function_code(keywords, description)},
            "email": {
                "toEmail": "admin@company.com",
                "subject": f"Workflow: {description[:30]}",
                "message": f"Workflow completed for: {description}"
            },
            "http_request": {
                "url": "https://api.example.com/webhook",
                "method": "POST"
            },
            "slack": {
                "channel": "#notifications",
                "text": f"🤖 Workflow alert: {description[:50]}"
            }
        }
        
        return configs.get(node_type, {})
    
    def _generate_function_code(self, keywords: Dict, description: str) -> str:
        """Generate JavaScript code for function nodes"""
        if "score" in description.lower() or "qualify" in description.lower():
            return """
// Scoring and qualification logic
const items = $input.all();

return items.map(item => {
  const data = item.json;
  let score = 0;
  
  // Basic scoring logic
  if (data.email && data.email.includes('@')) score += 20;
  if (data.name && data.name.length > 2) score += 15;
  if (data.company) score += 25;
  if (data.phone) score += 10;
  
  return {
    ...data,
    score: score,
    qualified: score >= 50,
    processed_at: new Date().toISOString()
  };
});
"""
        elif "validate" in description.lower():
            return """
// Data validation logic
const items = $input.all();

return items.map(item => {
  const data = item.json;
  const errors = [];
  
  if (!data.email || !data.email.includes('@')) errors.push('Invalid email');
  if (!data.name || data.name.length < 2) errors.push('Name required');
  
  return {
    ...data,
    valid: errors.length === 0,
    errors: errors,
    validated_at: new Date().toISOString()
  };
});
"""
        else:
            return """
// Process and enrich data
const items = $input.all();

return items.map(item => ({
  ...item.json,
  processed: true,
  processed_at: new Date().toISOString(),
  workflow_id: $workflow.id
}));
"""
    
    def _create_node(self, node_type: str, name: str, position: List[int], config: Dict) -> Dict:
        """Create a node with proper n8n structure"""
        node_info = self.node_registry.get(node_type, self.node_registry["set"])
        
        base_node = {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": node_info["type"],
            "position": position,
            "typeVersion": 1
        }
        
        # Add node-specific parameters
        parameters = {**node_info["default_params"], **config}
        if parameters:
            base_node["parameters"] = parameters
        
        # Add credentials if needed
        if node_type in ["hubspot", "salesforce", "slack", "email_send"]:
            base_node["credentials"] = self._get_node_credentials(node_type)
        
        return base_node
    
    def _get_node_credentials(self, node_type: str) -> Dict:
        """Get credentials configuration for node type"""
        cred_mapping = {
            "hubspot": {"hubspotApi": {"id": "1", "name": "HubSpot account"}},
            "salesforce": {"salesforceOAuth2Api": {"id": "1", "name": "Salesforce account"}},
            "slack": {"slackApi": {"id": "1", "name": "Slack account"}},
            "email_send": {"smtp": {"id": "1", "name": "SMTP account"}}
        }
        return cred_mapping.get(node_type, {})
    
    def _create_connections(self, nodes: List[Dict]) -> Dict:
        """Create connections between nodes"""
        connections = {}
        
        for i in range(len(nodes) - 1):
            current_node = nodes[i]["name"]
            next_node = nodes[i + 1]["name"]
            
            connections[current_node] = {
                "main": [[{"node": next_node, "type": "main", "index": 0}]]
            }
        
        return connections
    
    def _build_workflow(self, description: str, nodes: List[Dict], connections: Dict) -> Dict[str, Any]:
        """Build complete workflow structure"""
        return {
            "id": str(uuid.uuid4()),
            "name": self._generate_workflow_name(description),
            "active": False,
            "nodes": nodes,
            "connections": connections,
            "settings": {"executionOrder": "v1"},
            "staticData": {},
            "tags": [],
            "triggerCount": 1,
            "updatedAt": datetime.now().isoformat(),
            "versionId": str(uuid.uuid4()),
            "meta": {
                "description": description,
                "generated_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "generator_version": "enhanced_v1.0"
            }
        }
    
    def _generate_workflow_name(self, description: str) -> str:
        """Generate workflow name from description"""
        # Clean and format description
        clean_desc = re.sub(r'[^a-zA-Z0-9\s]', '', description)
        words = clean_desc.split()[:4]  # Take first 4 words
        return " ".join(word.capitalize() for word in words) + " Workflow"
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response to extract JSON"""
        try:
            # Clean response
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            raise
    
    def _enhance_workflow(self, workflow: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhance workflow with additional metadata and validation"""
        # Ensure required fields
        if 'id' not in workflow:
            workflow['id'] = str(uuid.uuid4())
        if 'name' not in workflow:
            workflow['name'] = self._generate_workflow_name(description)
        if 'settings' not in workflow:
            workflow['settings'] = {"executionOrder": "v1"}
        if 'staticData' not in workflow:
            workflow['staticData'] = {}
        
        # Add metadata
        workflow['meta'] = {
            "description": description,
            "generated_at": datetime.now().isoformat(),
            "node_count": len(workflow.get('nodes', [])),
            "generator_version": "enhanced_v1.0"
        }
        
        # Ensure proper node IDs
        for node in workflow.get('nodes', []):
            if 'id' not in node:
                node['id'] = str(uuid.uuid4())
        
        return workflow
    
    def _generate_fallback_workflow(self, description: str) -> Dict[str, Any]:
        """Generate simple fallback workflow"""
        print("🔄 Generating fallback workflow")
        
        return {
            "id": str(uuid.uuid4()),
            "name": f"Fallback - {description[:30]}",
            "active": False,
            "nodes": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Start",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300],
                    "parameters": {
                        "path": "/fallback-webhook",
                        "httpMethod": "POST"
                    },
                    "typeVersion": 1
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Process",
                    "type": "n8n-nodes-base.function",
                    "position": [460, 300],
                    "parameters": {
                        "functionCode": f"""
// Fallback processing for: {description}
const items = $input.all();
return items.map(item => ({{
  ...item.json,
  processed: true,
  description: '{description}',
  fallback: true,
  timestamp: new Date().toISOString()
}}));
"""
                    },
                    "typeVersion": 1
                }
            ],
            "connections": {
                "Start": {
                    "main": [[{"node": "Process", "type": "main", "index": 0}]]
                }
            },
            "settings": {"executionOrder": "v1"},
            "staticData": {},
            "tags": ["fallback"],
            "triggerCount": 1,
            "updatedAt": datetime.now().isoformat(),
            "versionId": str(uuid.uuid4())
        }
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive workflow validation"""
        errors = []
        warnings = []
        
        try:
            # Check required fields
            required_fields = ["name", "nodes", "connections"]
            for field in required_fields:
                if field not in workflow:
                    errors.append(f"Missing required field: {field}")
            
            # Validate nodes
            if "nodes" in workflow:
                if not workflow["nodes"]:
                    errors.append("Workflow must have at least one node")
                
                node_names = []
                for i, node in enumerate(workflow["nodes"]):
                    # Check node structure
                    node_required = ["id", "name", "type", "position"]
                    for field in node_required:
                        if field not in node:
                            errors.append(f"Node {i} missing required field: {field}")
                    
                    # Check for duplicate names
                    node_name = node.get("name", f"Node {i}")
                    if node_name in node_names:
                        errors.append(f"Duplicate node name: {node_name}")
                    node_names.append(node_name)
                
                # Check for trigger nodes
                trigger_types = ["webhook", "manualTrigger", "scheduleTrigger"]
                has_trigger = any(
                    any(trigger in node.get("type", "") for trigger in trigger_types)
                    for node in workflow["nodes"]
                )
                if not has_trigger:
                    warnings.append("Workflow should have at least one trigger node")
            
            # Validate connections
            if "connections" in workflow and "nodes" in workflow:
                node_names = [node["name"] for node in workflow["nodes"]]
                
                for source_node, connections in workflow["connections"].items():
                    if source_node not in node_names:
                        errors.append(f"Connection references non-existent node: {source_node}")
                    
                    if "main" in connections:
                        for connection_group in connections["main"]:
                            for connection in connection_group:
                                target_node = connection.get("node")
                                if target_node and target_node not in node_names:
                                    errors.append(f"Connection references non-existent target: {target_node}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "node_count": len(workflow.get("nodes", [])),
                "connection_count": len(workflow.get("connections", {}))
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "node_count": 0,
                "connection_count": 0
            }
    
    def get_workflow_summary(self, workflow: Dict[str, Any]) -> str:
        """Generate workflow summary"""
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})
        
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown").split(".")[-1]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        type_summary = ", ".join([f"{count} {type}" for type, count in node_types.items()])
        
        return f"""
📋 Workflow: {workflow.get('name', 'Unnamed')}
🔧 Nodes: {len(nodes)} ({type_summary})
🔗 Connections: {len(connections)}
🎯 Ready for deployment to n8n

🔄 Generated at: {workflow.get('meta', {}).get('generated_at', 'Unknown')}
"""
    
    def create_workflow_with_debug(self, description):
        """Create workflow with debug logging"""
        
        # Generate workflow using the existing method
        workflow = self.generate_workflow_from_description(description)
        
        # Add debug logging
        debug_dir = "workflow_generator_debug"
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_name = workflow.get('name', 'Generated_Workflow')
        
        json_file = os.path.join(debug_dir, f"GENERATED_{workflow_name.replace(' ', '_')}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        print(f"\n🔍 WORKFLOW GENERATOR DEBUG:")
        print(f"📝 Generated JSON: {json_file}")
        print(f"📊 Description: {description}")
        print(f"🏷️ Name: {workflow_name}")
        
        # Analyze the structure
        if 'nodes' in workflow:
            print(f"🔢 Generated {len(workflow['nodes'])} nodes:")
            for i, node in enumerate(workflow['nodes'][:5]):  # Show first 5
                print(f"   {i+1}. {node.get('name', 'Unnamed')} ({node.get('type', 'Unknown')})")
            if len(workflow['nodes']) > 5:
                print(f"   ... and {len(workflow['nodes']) - 5} more")
        else:
            print("⚠️ WARNING: No 'nodes' array in generated workflow!")
        
        if 'connections' in workflow:
            print(f"🔗 Generated {len(workflow['connections'])} connection groups")
        else:
            print("⚠️ WARNING: No 'connections' object in generated workflow!")
        
        return workflow


# MOVED OUTSIDE THE CLASS - This fixes the error
def test_enhanced_generator():
    """Test the enhanced workflow generator"""
    print("🧪 Testing Enhanced N8N Workflow Generator...")
    
    try:
        generator = EnhancedN8nWorkflowGenerator()
        
        # Test different workflow types
        test_descriptions = [
            "Create a lead qualification workflow with CRM integration",
            "Process customer feedback and send notifications",
            "Automate invoice processing with approval workflow",
            "Social media post scheduling with content validation"
        ]
        
        for description in test_descriptions:
            print(f"\n🔄 Testing: {description}")
            
            # Generate workflow
            workflow = generator.generate_workflow_from_description(description)
            
            # Validate
            validation = generator.validate_workflow(workflow)
            
            # Print results
            print(f"✅ Generated: {validation['node_count']} nodes, {validation['connection_count']} connections")
            print(f"📊 Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
            
            if validation['errors']:
                print(f"❌ Errors: {validation['errors']}")
            
            # Print summary
            print(generator.get_workflow_summary(workflow))
        
        print("\n🎉 Enhanced workflow generator test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# This ensures the test runs when the file is executed directly
if __name__ == "__main__":
    test_enhanced_generator()