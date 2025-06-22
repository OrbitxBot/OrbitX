import chromadb
import json
import sys

def setup_workflows_in_chroma():
    try:
        print("🔌 Connecting to ChromaDB server...")
        # Connect to local ChromaDB server
        client = chromadb.HttpClient(host="localhost", port=8000)
        
        # Test connection
        client.heartbeat()
        print("✅ Connected to ChromaDB server!")
        
        # Create or get collection
        print("📁 Creating/accessing collection...")
        collection = client.get_or_create_collection(
            name="n8n_workflows",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Load workflow metadata
        print("📖 Loading workflow metadata...")
        with open('workflow_metadata.json', 'r') as f:
            data = json.load(f)
            workflows = data['workflows_metadata']  # Extract the workflows array
        
        # Clear existing data (optional - uncomment if needed)
        # print("🗑️ Clearing existing data...")
        # collection.delete()
        
        # Prepare data for batch insertion
        ids = []
        documents = []
        metadatas = []
        
        print("🔄 Processing workflows...")
        for i, wf in enumerate(workflows):
            # Create unique ID since your data doesn't have IDs
            workflow_id = f"w{i+1}"
            
            # Create searchable document text
            document_text = f"""
            Title: {wf['title']}
            Description: {wf['description']}
            Domain: {wf['domain']}
            Tags: {', '.join(wf['tags'])}
            Parameters: {', '.join(wf['parameter_types'])}
            """.strip()
            
            # FIX: Convert lists to strings for ChromaDB compatibility
            metadata_with_id = {
                'id': workflow_id,
                'title': wf['title'],
                'description': wf['description'],
                'domain': wf['domain'],
                'tags': ', '.join(wf['tags']),  # Convert list to comma-separated string
                'parameter_types': ', '.join(wf['parameter_types'])  # Convert list to comma-separated string
            }
            
            ids.append(workflow_id)
            documents.append(document_text)
            metadatas.append(metadata_with_id)
        
        # Insert all workflows at once
        print("💾 Storing workflows in ChromaDB...")
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # Verify insertion
        count = collection.count()
        print(f"✅ Successfully stored {count} workflows in ChromaDB!")
        
        # Test a sample query
        print("\n🔍 Testing search functionality...")
        results = collection.query(
            query_texts=["help me with employee onboarding and setup"],
            n_results=2
        )
        
        print("Sample search results:")
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            print(f"  {i+1}. {metadata['title']} (similarity: {1-distance:.3f})")
            
    except FileNotFoundError:
        print("❌ Error: workflow_metadata.json not found!")
        print("   Make sure the file exists in the current directory.")
        sys.exit(1)
        
    except Exception as e:
        if "Connection refused" in str(e):
            print("❌ Error: Cannot connect to ChromaDB server!")
            print("   Make sure you started the server with: chroma run --path ./chroma_data --port 8000")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_workflows_in_chroma()