from langchain.agents import initialize_agent, Tool, AgentType
from langchain_mistralai import ChatMistralAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
import os
import json
from typing import Dict, Any, List
import uuid
import json
import os
from datetime import datetime

import json
import os
from pathlib import Path
from datetime import datetime

# Import our custom classes
from chromadb_client import WorkflowChromaDB
from n8n_api_client import N8nAPIClient
from workflow_generator import EnhancedN8nWorkflowGenerator
from mistralai import Mistral

class WorkflowGeneratorAgent:
    def __init__(self, mistral_api_key: str, n8n_base_url: str, n8n_api_key: str = None, 
             chroma_host: str = "localhost", chroma_port: int = 8000):
        """Initialize the Workflow Generator Agent with Mistral AI"""

        # Initialize Mistral AI LLM
        self.llm = ChatMistralAI(
            mistral_api_key=mistral_api_key,
            model="mistral-medium",  # You can change to mistral-small or mistral-large
            temperature=0.7
        )

        # Initialize Mistral client for enhanced generator (THIS WAS MISSING!)
        self.client = Mistral(api_key=mistral_api_key)

        # Initialize clients
        self.chroma_client = WorkflowChromaDB(host=chroma_host, port=chroma_port)
        self.n8n_client = N8nAPIClient(n8n_base_url, n8n_api_key)

        # Initialize enhanced generator with the correct client
        self.enhanced_generator = EnhancedN8nWorkflowGenerator(mistral_client=self.client)

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize storage for generated workflows
        self.last_generated_workflow = None
        self.current_workflow = None

        # Initialize agent with tools - FIXED: Use the correct method names with underscores
        self.tools = [
            Tool(
                name="search_similar_workflows",
                description="Search for similar workflows in the database",
                func=self._search_similar_workflows  # FIXED: Added underscore
            ),
            Tool(
                name="generate_workflow", 
                description="Generate a new n8n workflow based on user requirements",
                func=self._generate_workflow  # FIXED: Added underscore
            ),
            Tool(
                name="deploy_workflow",
                description="Deploy the generated workflow to n8n with debug logging",
                func=self.debug_and_deploy  # This one is correct
            ),
            Tool(
                name="get_collection_stats",
                description="Get statistics about the workflow collection",
                func=self._get_collection_stats  # FIXED: Added underscore
            )
        ]
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )

        print("✅ Workflow Generator Agent initialized with Mistral AI!")

    def debug_and_deploy(self, workflow_request="deploy"):
        """Enhanced deployment with JSON logging - ADD THIS METHOD"""
        try:
            if not hasattr(self, 'last_generated_workflow') or not self.last_generated_workflow:
                return "❌ No workflow to deploy. Generate one first."
            
            workflow_data = self.last_generated_workflow
            workflow_name = workflow_data.get('name', 'Generated_Workflow')
            
            # Create debug directory
            debug_dir = "workflow_debug_logs"
            os.makedirs(debug_dir, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Log the complete workflow JSON
            json_file = os.path.join(debug_dir, f"{workflow_name.replace(' ', '_')}_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n🔍 DEPLOYMENT DEBUG INFO:")
            print(f"📄 JSON saved to: {json_file}")
            print(f"📊 Workflow: {workflow_name}")
            print(f"🔢 Nodes: {len(workflow_data.get('nodes', []))}")
            print(f"🔗 Connections: {len(workflow_data.get('connections', {}))}")
            
            # Show node details
            if 'nodes' in workflow_data:
                print(f"\n📋 NODE DETAILS:")
                for i, node in enumerate(workflow_data['nodes']):
                    print(f"   {i+1}. {node.get('name', 'Unnamed')} ({node.get('type', 'Unknown')})")
            
            # Show connection details
            if 'connections' in workflow_data:
                print(f"\n🔗 CONNECTION DETAILS:")
                for source, targets in workflow_data['connections'].items():
                    if 'main' in targets and targets['main']:
                        for target_list in targets['main']:
                            for target in target_list:
                                print(f"   {source} → {target.get('node', 'Unknown')}")
            
            # Show structure
            json_preview = json.dumps(workflow_data, indent=2)
            print(f"\n📋 JSON PREVIEW (first 1200 chars):")
            print("=" * 60)
            print(json_preview[:1200])
            if len(json_preview) > 1200:
                print("\n... (see full JSON in log file)")
            print("=" * 60)
            
            # Deploy
            print(f"\n🚀 Deploying to n8n...")
            result = self.n8n_client.create_workflow(workflow_data)
            
            # Log result
            result_file = os.path.join(debug_dir, f"{workflow_name.replace(' ', '_')}_result_{timestamp}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"📥 Result saved to: {result_file}")
            print(f"📊 Deployment status: {result.get('status', 'Unknown')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Debug deployment error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def debug_any_workflow_json(workflow_data, source_name="Unknown"):
        """Standalone function to debug any workflow JSON"""
    
        debug_dir = "standalone_debug"
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(debug_dir, f"{source_name}_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🔍 DEBUG: {source_name}")
        print(f"📄 JSON saved: {filename}")
        print(f"📊 Structure: {list(workflow_data.keys())}")
        
        if 'nodes' in workflow_data:
            nodes = workflow_data['nodes']
            print(f"🔢 Nodes ({len(nodes)}):")
            for node in nodes[:3]:
                print(f"   • {node.get('name', 'Unnamed')} - {node.get('type', 'Unknown type')}")
            if len(nodes) > 3:
                print(f"   • ... and {len(nodes)-3} more")
        
        if 'connections' in workflow_data:
            connections = workflow_data['connections']
            print(f"🔗 Connections ({len(connections)} groups)")
        
        # Show JSON preview
        json_str = json.dumps(workflow_data, indent=2)
        print(f"\n📋 JSON PREVIEW:")
        print("-" * 40)
        print(json_str[:600])
        if len(json_str) > 600:
            print("... (see full JSON in file)")
        print("-" * 40)
        
        return filename
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        return [
            Tool(
                name="search_similar_workflows",
                description="Search for similar existing workflows based on description and domain. Input should be a search query string.",
                func=self._search_similar_workflows
            ),
            Tool(
                name="generate_workflow",
                description="Generate a new n8n workflow based on requirements. Input should be the workflow requirements description.",
                func=self._generate_workflow
            ),
            Tool(
                name="deploy_workflow",
                description="Deploy the last generated workflow to n8n. Input should be 'deploy' or confirmation message.",
                func=self._deploy_workflow
            ),
            Tool(
                name="get_domain_workflows",
                description="Get all workflows for a specific domain (HR, Marketing, CRM, Sales, IT). Input should be the domain name.",
                func=self._get_domain_workflows
            ),
            Tool(
                name="get_collection_stats",
                description="Get statistics about the workflow collection. No input required.",
                func=self._get_collection_stats
            )
        ]
    
    def _search_similar_workflows(self, query: str) -> str:
        """Search for similar workflows in ChromaDB"""
        try:
            # Extract domain if mentioned
            domain = None
            domains = ["HR", "Marketing", "CRM", "Sales", "IT"]
            query_lower = query.lower()
            
            for d in domains:
                if d.lower() in query_lower:
                    domain = d
                    break
            
            similar_workflows = self.chroma_client.search_similar_workflows(query, domain, n_results=3)
            
            if similar_workflows:
                result = f"🔍 Found {len(similar_workflows)} similar workflows:\n\n"
                for i, workflow in enumerate(similar_workflows, 1):
                    similarity = workflow.get('similarity', 0)
                    result += f"{i}. **{workflow.get('title', 'Unknown')}** ({workflow.get('domain', 'Unknown')})\n"
                    result += f"   Similarity: {similarity:.3f}\n"
                    result += f"   Description: {workflow.get('description', 'No description')}\n"
                    result += f"   Tags: {workflow.get('tags', 'None')}\n\n"
                return result
            else:
                return "❌ No similar workflows found. This might be a new type of workflow!"
                
        except Exception as e:
            return f"❌ Error searching workflows: {str(e)}"
    
    def _generate_workflow(self, description: str) -> str:
        """Generate a complete n8n workflow JSON based on any description using Enhanced AI"""
        try:
            print(f"🤖 Generating enhanced workflow for: {description}")
        
            # Use the enhanced workflow generator with AI capabilities
            workflow_json = self.enhanced_generator.generate_workflow_from_description(description)
        
            # Store the generated workflow for deployment - FIXED: Ensure it's stored properly
            self.last_generated_workflow = workflow_json
            self.current_workflow = workflow_json
            
            # NEW: Immediately persist after generation
            self._ensure_workflow_persistence()
            
            # ADDED: Debug print to verify workflow is stored
            print(f"✅ Workflow stored: {workflow_json.get('name', 'Unknown')} with {len(workflow_json.get('nodes', []))} nodes")
        
            # Validate the generated workflow using enhanced validation
            validation = self.enhanced_generator.validate_workflow(workflow_json)
            if not validation['valid']:
                error_msg = f"❌ Workflow validation failed: {', '.join(validation['errors'])}"
                if validation['warnings']:
                    error_msg += f"\n⚠️ Warnings: {', '.join(validation['warnings'])}"
                return error_msg
        
            # Extract workflow details
            nodes = workflow_json.get('nodes', [])
            node_count = len(nodes)
            connections = workflow_json.get('connections', {})
            connection_count = len(connections)
        
            # Get node types for summary
            node_types = []
            for node in nodes:
                node_type = node.get('type', 'unknown')
                if '.' in node_type:
                    node_type = node_type.split('.')[-1]
                node_types.append(node_type)
        
            # Get unique node types
            unique_types = list(set(node_types))
        
            # Create detailed response with enhanced information
            workflow_name = workflow_json.get('name', 'Generated Workflow')
        
            result = f"""✅ **Enhanced N8N Workflow Generated Successfully!**

    📋 **Workflow Details:**
    • **Name:** {workflow_name}
    • **Nodes:** {node_count} nodes created
    • **Connections:** {connection_count} connections
    • **Node Types:** {', '.join(unique_types)}
    • **Generator:** Enhanced AI-powered generation

    🔗 **Workflow Structure:**"""
        
            # Add node details with enhanced information
            for i, node in enumerate(nodes[:6], 1):  # Show first 6 nodes
                node_name = node.get('name', f'Node {i}')
                node_type = node.get('type', 'unknown').split('.')[-1]
            
                # Add node description if available from registry
                node_desc = ""
                if hasattr(self.enhanced_generator, 'node_registry'):
                    registry_key = node_type.lower().replace('trigger', '').replace('nodes-base.', '')
                    if registry_key in self.enhanced_generator.node_registry:
                        node_desc = f" - {self.enhanced_generator.node_registry[registry_key].get('description', '')}"
            
                result += f"\n   {i}. {node_name} ({node_type}){node_desc}"
        
            if len(nodes) > 6:
                result += f"\n   ... and {len(nodes) - 6} more nodes"
        
            # Add webhook information if available
            webhook_nodes = [n for n in nodes if n.get('type', '').endswith('webhook')]
            if webhook_nodes:
                webhook_path = None
                for webhook in webhook_nodes:
                    path = webhook.get('parameters', {}).get('path', '')
                    if path:
                        webhook_path = path
                        break
            
                if webhook_path:
                    result += f"\n\n🌐 **Webhook Endpoint:** {webhook_path}"
        
            # Add AI-generated features information
            result += f"""

    🤖 **AI-Enhanced Features:**
    • Intelligent node selection based on description
    • Proper data flow and connections
    • Realistic parameters and configurations
    • Built-in validation and error handling
    • Context-aware JavaScript code generation

    📊 **Validation Results:**
    • Status: ✅ Valid workflow
    • Node Count: {validation.get('node_count', node_count)}
    • Connection Count: {validation.get('connection_count', connection_count)}"""
        
            # Add warnings if any
            if validation.get('warnings'):
                result += f"\n   • Warnings: {len(validation['warnings'])} items"
        
            result += f"""

    🚀 **Ready for Deployment!**
    Type 'deploy' to deploy this workflow to your n8n instance.

    **Enhanced AI-generated workflow JSON created and validated successfully.**"""
        
            print(f"✅ Enhanced workflow generated: {node_count} nodes, {connection_count} connections")
            print(f"✅ Workflow '{workflow_name}' generated and persisted successfully!")
            
            # ADDED: Double-check the workflow is properly stored
            if not self.last_generated_workflow:
                print("⚠️ WARNING: Workflow not properly stored in last_generated_workflow")
            else:
                print(f"✅ Workflow properly stored: {self.last_generated_workflow.get('name', 'Unknown')}")
                
            return result
        
        except Exception as e:
            error_msg = f"❌ Error generating enhanced workflow: {str(e)}"
            print(error_msg)
            # Fallback to basic generation if enhanced fails
            try:
                print("🔄 Attempting fallback generation...")
                fallback_workflow = self.enhanced_generator._generate_fallback_workflow(description)
                # FIXED: Store fallback workflow too
                self.last_generated_workflow = fallback_workflow
                self.current_workflow = fallback_workflow
                
                # NEW: Persist fallback workflow too
                self._ensure_workflow_persistence()
                
                print(f"✅ Fallback workflow stored: {fallback_workflow.get('name', 'Unknown')}")
                
                return f"""⚠️ **Fallback Workflow Generated**

    Due to an error in enhanced generation, a basic workflow was created:
    • Name: {fallback_workflow.get('name', 'Fallback Workflow')}
    • Nodes: {len(fallback_workflow.get('nodes', []))}
    • Status: Ready for deployment

    Use 'deploy' to deploy this fallback workflow."""
            except Exception as fallback_error:
                return f"❌ Both enhanced and fallback generation failed: {str(fallback_error)}"
    
    def _generate_custom_workflow(self, description: str) -> Dict[str, Any]:
        """Generate a custom workflow when no specific type is detected"""
        try:
            # Analyze description for common patterns
            description_lower = description.lower()
            
            # Determine components needed
            has_webhook = any(word in description_lower for word in ['form', 'submit', 'receive', 'trigger', 'webhook'])
            has_email = any(word in description_lower for word in ['email', 'notify', 'send', 'notification'])
            has_api = any(word in description_lower for word in ['api', 'integration', 'connect', 'http'])
            has_condition = any(word in description_lower for word in ['if', 'condition', 'check', 'approve', 'decide'])
            has_data_processing = any(word in description_lower for word in ['process', 'transform', 'calculate', 'filter'])
            has_database = any(word in description_lower for word in ['database', 'save', 'store', 'record'])
            has_slack = any(word in description_lower for word in ['slack', 'chat', 'message', 'team'])
            
            # Use the workflow generator's basic workflow method with enhanced configuration
            nodes_config = []
            
            # Add data processing if needed
            if has_data_processing:
                nodes_config.append({
                    "type": "function",
                    "name": "Process Data",
                    "code": """// Process and transform incoming data
const processedItems = items.map(item => {
  const data = item.json;
  return {
    json: {
      ...data,
      processed_at: new Date().toISOString(),
      processed: true,
      workflow_id: '{{$workflow.id}}',
      // Add your custom processing logic here
    }
  };
});

return processedItems;"""
                })
            
            # Add conditional logic if needed
            if has_condition:
                nodes_config.append({
                    "type": "switch",
                    "name": "Decision Point",
                    "rules": [
                        {"condition": "processed", "value": True},
                        {"condition": "priority", "value": "high"}
                    ]
                })
            
            # Add API integration if needed
            if has_api:
                nodes_config.append({
                    "type": "http",
                    "name": "API Integration",
                    "url": "https://api.example.com/webhook",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                })
            
            # Add database storage if needed
            if has_database:
                nodes_config.append({
                    "type": "set",
                    "name": "Store Data",
                    "variables": [
                        {"name": "record_id", "value": "{{$json.id}}"},
                        {"name": "stored_at", "value": "{{new Date().toISOString()}}"}
                    ]
                })
            
            # Add Slack notification if needed
            if has_slack:
                nodes_config.append({
                    "type": "slack",
                    "name": "Slack Notification",
                    "channel": "#general",
                    "message": f"🤖 Workflow executed: {description[:50]}..."
                })
            
            # Add email notification if needed
            if has_email:
                nodes_config.append({
                    "type": "email",
                    "name": "Email Notification",
                    "to_email": "admin@company.com",
                    "subject": f"Workflow Notification: {description[:30]}...",
                    "message": f"Workflow completed successfully.\n\nDescription: {description}\nTimestamp: {{{{new Date().toISOString()}}}}"
                })
            
            # If no specific components detected, add basic processing
            if not nodes_config:
                nodes_config = [
                    {
                        "type": "set",
                        "name": "Process Request",
                        "variables": [
                            {"name": "timestamp", "value": "{{new Date().toISOString()}}"},
                            {"name": "status", "value": "processed"},
                            {"name": "description", "value": description}
                        ]
                    },
                    {
                        "type": "email",
                        "name": "Send Notification",
                        "to_email": "admin@company.com",
                        "subject": "Custom Workflow Executed",
                        "message": f"Custom workflow executed: {description}"
                    }
                ]
            
            # Generate the workflow using the basic workflow method
            webhook_path = "/custom-workflow"
            if has_webhook:
                # Extract potential webhook path from description
                words = description.split()
                for word in words:
                    if word.startswith('/') or 'webhook' in word.lower():
                        webhook_path = f"/{word.replace('/', '').lower().replace(' ', '-')}"
                        break
            
            workflow_data = self.workflow_generator.generate_basic_workflow(
                title=f"Custom Workflow - {description[:40]}...",
                description=description,
                domain="Custom",
                webhook_path=webhook_path,
                nodes_config=nodes_config
            )
            
            return workflow_data
            
        except Exception as e:
            print(f"Error in _generate_custom_workflow: {e}")
            # Fallback to very basic workflow
            return self.workflow_generator.generate_basic_workflow(
                title="Basic Custom Workflow",
                description=description,
                domain="Custom",
                webhook_path="/basic-webhook",
                nodes_config=[
                    {
                        "type": "set",
                        "name": "Process Data",
                        "variables": [{"name": "processed", "value": "true"}]
                    }
                ]
            )
    
    def _deploy_workflow(self, action: str) -> str:
        """Deploy the generated workflow to n8n"""
        try:
            if not hasattr(self, 'last_generated_workflow') or not self.last_generated_workflow:
                return "❌ No workflow available for deployment. Please generate a workflow first."
            
            print(f"🚀 Starting deployment process...")
            
            # Clean the workflow data - remove read-only fields
            workflow_data = self.last_generated_workflow.copy()
            
            # Remove read-only fields that cause API errors
            fields_to_remove = ['active', 'id', 'createdAt', 'updatedAt', 'versionId']
            for field in fields_to_remove:
                if field in workflow_data:
                    del workflow_data[field]
            
            # Ensure required fields are present
            if 'settings' not in workflow_data:
                workflow_data['settings'] = {"executionOrder": "v1"}
            if 'staticData' not in workflow_data:
                workflow_data['staticData'] = {}
            if 'connections' not in workflow_data:
                workflow_data['connections'] = {}
            if 'tags' not in workflow_data:
                workflow_data['tags'] = []
            
            workflow_name = workflow_data.get('name', 'Generated Workflow')
            node_count = len(workflow_data.get('nodes', []))
            connection_count = len(workflow_data.get('connections', {}))
            
            print(f"🚀 Deploying: {workflow_name} ({node_count} nodes, {connection_count} connections)")
            
            # Deploy using n8n API client
            result = self.n8n_client.create_workflow(workflow_data)
            
            if result["status"] == "success":
                workflow_id = result["id"]
                
                # Try to get webhook URL if available
                webhook_info = ""
                webhook_nodes = [n for n in workflow_data.get('nodes', []) if n.get('type', '').endswith('webhook')]
                if webhook_nodes:
                    webhook_path = None
                    for webhook in webhook_nodes:
                        path = webhook.get('parameters', {}).get('path', '')
                        if path:
                            webhook_path = path
                            break
                    
                    if webhook_path:
                        base_url = self.n8n_client.base_url.replace('/api/v1', '')
                        webhook_url = f"{base_url}/webhook{webhook_path}"
                        webhook_info = f"\n🌐 **Webhook URL:** {webhook_url}"
                
                return f"""🎉 **Workflow Deployed Successfully!**

📋 **Deployment Details:**
   • **Workflow ID:** {workflow_id}
   • **Workflow Name:** {workflow_name}
   • **Nodes Deployed:** {node_count} nodes
   • **Connections:** {connection_count} connections
   • **Status:** Created (Inactive){webhook_info}

🔧 **Next Steps:**
   1. Visit your n8n dashboard to activate the workflow
   2. Configure any required credentials
   3. Test the workflow with sample data

✅ **Deployment Complete!** Your workflow is now available in n8n.
"""
            else:
                return f"❌ Deployment failed: {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            error_msg = f"❌ Deployment error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _get_domain_workflows(self, domain: str) -> str:
        """Get all workflows for a specific domain"""
        try:
            workflows = self.chroma_client.get_all_workflows_by_domain(domain.upper())
            
            if workflows:
                result = f"📁 **{domain.upper()} Domain Workflows** ({len(workflows)} found):\n\n"
                for i, workflow in enumerate(workflows, 1):
                    result += f"{i}. **{workflow.get('title', 'Unknown')}**\n"
                    result += f"   Description: {workflow.get('description', 'No description')}\n"
                    result += f"   Tags: {workflow.get('tags', 'None')}\n\n"
                return result
            else:
                return f"❌ No workflows found in {domain.upper()} domain."
                
        except Exception as e:
            return f"❌ Error retrieving workflows: {str(e)}"
    
    def _get_collection_stats(self, _: str = "") -> str:
        """Get collection statistics"""
        try:
            stats = self.chroma_client.get_collection_stats()
            
            result = f"📊 **Workflow Collection Statistics**\n\n"
            result += f"📈 **Total Workflows:** {stats.get('total_workflows', 0)}\n\n"
            
            if 'domain_distribution' in stats:
                result += "🏢 **Domain Distribution:**\n"
                for domain, count in stats['domain_distribution'].items():
                    result += f"   • {domain}: {count} workflows\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error getting collection stats: {str(e)}"
    
    def process_request(self, user_input):
        """Process user request and generate workflow with persistent storage"""
        try:
            # Existing code for system prompt and agent execution
            system_prompt = self._create_system_prompt()
            response = self.agent.run(f"{system_prompt}\n\nUser request: {user_input}")
            
            # NEW: After agent execution, ensure workflow is persisted
            self._ensure_workflow_persistence()
            
            return response
        except Exception as e:
            print(f"❌ Error in process_request: {str(e)}")
            return f"Error processing request: {str(e)}"
        
    def _ensure_workflow_persistence(self):
        """Ensure generated workflow is stored in multiple locations"""
        if self.last_generated_workflow:
            try:
                # Create workflows directory if it doesn't exist
                workflows_dir = Path("generated_workflows")
                workflows_dir.mkdir(exist_ok=True)
                
                # Save to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"workflow_{timestamp}.json"
                filepath = workflows_dir / filename
                
                # Save workflow to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_generated_workflow, f, indent=2, ensure_ascii=False)
                
                # Also save as "latest" for easy access
                latest_filepath = workflows_dir / "latest_workflow.json"
                with open(latest_filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_generated_workflow, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Workflow persisted to: {filepath}")
                print(f"✅ Latest workflow saved to: {latest_filepath}")
                
            except Exception as e:
                print(f"❌ Error persisting workflow: {str(e)}")
        


    def validate_workflow_json(self, workflow_data):
        """Validate that the workflow JSON is properly formatted"""
        if not workflow_data:
            return False, "No workflow data provided"
        
        if not isinstance(workflow_data, dict):
            return False, "Workflow must be a dictionary/JSON object"
        
        # Check for required fields (adjust based on your n8n requirements)
        required_fields = ['nodes', 'connections']  # Common n8n workflow fields
        
        for field in required_fields:
            if field not in workflow_data:
                return False, f"Missing required field: {field}"
        
        return True, "Workflow is valid"
    

    def _ensure_workflow_persistence(self):
        """Ensure generated workflow is stored in multiple locations"""
        if self.last_generated_workflow:
            try:
                # Create workflows directory if it doesn't exist
                workflows_dir = Path("generated_workflows")
                workflows_dir.mkdir(exist_ok=True)
                
                # Save to file with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"workflow_{timestamp}.json"
                filepath = workflows_dir / filename
                
                # Save workflow to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_generated_workflow, f, indent=2, ensure_ascii=False)
                
                # Also save as "latest" for easy access
                latest_filepath = workflows_dir / "latest_workflow.json"
                with open(latest_filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.last_generated_workflow, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Workflow persisted to: {filepath}")
                print(f"✅ Latest workflow saved to: {latest_filepath}")
                
            except Exception as e:
                print(f"❌ Error persisting workflow: {str(e)}")

    def load_latest_workflow(self):
        """Load the latest generated workflow from persistent storage"""
        try:
            latest_filepath = Path("generated_workflows") / "latest_workflow.json"
            
            if latest_filepath.exists():
                with open(latest_filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                
                self.last_generated_workflow = workflow_data
                print(f"✅ Loaded workflow: {workflow_data.get('name', 'Unknown')}")
                return workflow_data
            else:
                print("⚠️ No persisted workflow found")
                return None
                
        except Exception as e:
            print(f"❌ Error loading workflow: {str(e)}")
            return None

# Usage example and test
if __name__ == "__main__":
    from config import Config
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize the agent
        agent = WorkflowGeneratorAgent(
            mistral_api_key=Config.MISTRAL_API_KEY,
            n8n_base_url=Config.N8N_BASE_URL,
            n8n_api_key=Config.N8N_API_KEY,
            chroma_host=Config.CHROMA_HOST,
            chroma_port=Config.CHROMA_PORT
        )
        
        # Test the agent
        print("\n🤖 Testing Workflow Generator Agent...")
        response = agent.process_request("Create a workflow for processing customer feedback")
        print(f"\n🤖 Agent Response:\n{response}")
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("\n📋 Checklist:")
        print("1. ✅ ChromaDB server running? (chroma run --path ./chroma_data --port 8000)")
        print("2. ✅ Mistral API key in .env file?")
        print("3. ✅ Workflow metadata loaded in ChromaDB?")