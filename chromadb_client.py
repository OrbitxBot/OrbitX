import chromadb
import json
from typing import List, Dict, Any

class WorkflowChromaDB:
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize ChromaDB client for server connection"""
        self.client = chromadb.HttpClient(host=host, port=port)
        
        # Test connection
        try:
            self.client.heartbeat()
            print("✅ Connected to ChromaDB server!")
        except Exception as e:
            print(f"❌ Failed to connect to ChromaDB server: {e}")
            raise
        
        # Get the existing collection (created by your setup script)
        try:
            self.collection = self.client.get_collection(name="n8n_workflows")
            print(f"✅ Connected to collection with {self.collection.count()} workflows")
        except Exception as e:
            print(f"❌ Failed to get collection: {e}")
            raise
    
    def store_workflow(self, workflow_data: Dict[str, Any]):
        """Store workflow metadata in ChromaDB"""
        workflow_id = workflow_data.get("id", f"generated_{len(self.get_all_workflows()) + 1}")
        title = workflow_data.get("title", "")
        description = workflow_data.get("description", "")
        domain = workflow_data.get("domain", "")
        tags = workflow_data.get("tags", [])
        parameter_types = workflow_data.get("parameter_types", [])
        
        # Create searchable document text
        document_text = f"""
        Title: {title}
        Description: {description}
        Domain: {domain}
        Tags: {', '.join(tags) if isinstance(tags, list) else tags}
        Parameters: {', '.join(parameter_types) if isinstance(parameter_types, list) else parameter_types}
        """.strip()
        
        # Prepare metadata (convert lists to strings for ChromaDB compatibility)
        metadata = {
            'id': workflow_id,
            'title': title,
            'description': description,
            'domain': domain,
            'tags': ', '.join(tags) if isinstance(tags, list) else tags,
            'parameter_types': ', '.join(parameter_types) if isinstance(parameter_types, list) else parameter_types
        }
        
        # Add to collection
        self.collection.add(
            ids=[workflow_id],
            documents=[document_text],
            metadatas=[metadata]
        )
        
        print(f"✅ Stored workflow: {title} in domain: {domain}")
    
    def search_similar_workflows(self, query: str, domain: str = None, n_results: int = 3) -> List[Dict]:
        """Search for similar workflows based on query"""
        try:
            # Prepare where filter if domain is specified
            where_filter = {"domain": domain} if domain else None
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            similar_workflows = []
            if results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    # Add similarity score
                    similarity = 1 - results['distances'][0][i] if results['distances'] else 1.0
                    workflow_info = metadata.copy()
                    workflow_info['similarity'] = similarity
                    similar_workflows.append(workflow_info)
            
            return similar_workflows
            
        except Exception as e:
            print(f"❌ Error searching workflows: {e}")
            return []
    
    def get_all_workflows_by_domain(self, domain: str) -> List[Dict]:
        """Get all workflows for a specific domain"""
        try:
            results = self.collection.get(
                where={"domain": domain}
            )
            
            workflows = []
            if results['metadatas']:
                workflows = results['metadatas']
            
            return workflows
            
        except Exception as e:
            print(f"❌ Error getting workflows by domain: {e}")
            return []
    
    def get_all_workflows(self) -> List[Dict]:
        """Get all workflows"""
        try:
            results = self.collection.get()
            return results['metadatas'] if results['metadatas'] else []
        except Exception as e:
            print(f"❌ Error getting all workflows: {e}")
            return []
    
    def get_workflow_by_id(self, workflow_id: str) -> Dict:
        """Get specific workflow by ID"""
        try:
            results = self.collection.get(ids=[workflow_id])
            
            if results['metadatas'] and results['metadatas'][0]:
                return results['metadatas'][0]
            return {}
            
        except Exception as e:
            print(f"❌ Error getting workflow by ID: {e}")
            return {}
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        try:
            total_count = self.collection.count()
            
            # Get domain distribution
            all_workflows = self.get_all_workflows()
            domain_counts = {}
            for wf in all_workflows:
                domain = wf.get('domain', 'Unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            return {
                'total_workflows': total_count,
                'domain_distribution': domain_counts
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

# Test the ChromaDB connection
if __name__ == "__main__":
    try:
        # Initialize ChromaDB client
        chroma_client = WorkflowChromaDB()
        
        # Get stats
        stats = chroma_client.get_collection_stats()
        print(f"📊 Collection Stats: {stats}")
        
        # Test search
        print("\n🔍 Testing search...")
        results = chroma_client.search_similar_workflows("employee onboarding", n_results=2)
        
        for result in results:
            print(f"  - {result['title']} ({result['domain']}) - Similarity: {result['similarity']:.3f}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure ChromaDB server is running: chroma run --path ./chroma_data --port 8000")