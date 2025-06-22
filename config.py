# config.py
import os
from dotenv import load_dotenv
from mistralai import Mistral


# ...existing code...

# Load environment variables from .env file
load_dotenv()

class Config:
    # Mistral AI Configuration
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium")
    
    # n8n Configuration
    N8N_BASE_URL = os.getenv("N8N_BASE_URL")
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    
    # ChromaDB Configuration (Server mode)
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
    
    # Workflow Configuration
    DEFAULT_DOMAINS = ["HR", "Marketing", "CRM", "Sales", "IT"]
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        missing = []
        
        if not cls.MISTRAL_API_KEY:
            missing.append("MISTRAL_API_KEY")
        
        if not cls.N8N_BASE_URL:
            missing.append("N8N_BASE_URL")
            
        if not cls.N8N_API_KEY:
            missing.append("N8N_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print("✅ Configuration validation successful!")
        print(f"✅ Mistral API Key: {'*' * 20}...{cls.MISTRAL_API_KEY[-4:] if cls.MISTRAL_API_KEY else 'NOT SET'}")
        print(f"✅ n8n URL: {cls.N8N_BASE_URL}")
        print(f"✅ n8n API Key: {'*' * 20}...{cls.N8N_API_KEY[-4:] if cls.N8N_API_KEY else 'NOT SET'}")
        print(f"✅ ChromaDB: {cls.CHROMA_HOST}:{cls.CHROMA_PORT}")
        
        return True

    @classmethod
    def test_mistral_connection(cls):
        """Test Mistral API connection"""
        try:
            # Use the new Mistral client
            from mistralai import Mistral
            client = Mistral(api_key=cls.MISTRAL_API_KEY)
            
            # Simple test call with new client format
            response = client.chat.complete(
            model=cls.MISTRAL_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
            )
            print("✅ Mistral API connection successful!")
            return True
        except ImportError:
            print("⚠️  New Mistral client not available, trying legacy client...")
            try:
                from mistralai.client import MistralClient
                client = MistralClient(api_key=cls.MISTRAL_API_KEY)
                response = client.chat(
                    model=cls.MISTRAL_MODEL,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print("✅ Mistral API connection successful (legacy client)!")
                print("⚠️  Consider upgrading to new Mistral client version")
                return True
            except Exception as e:
                print(f"❌ Mistral API connection failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Mistral API connection failed: {e}")
            return False

# Test configuration when run directly
if __name__ == "__main__":
    print("🔧 Testing Configuration...")
    
    try:
        Config.validate_config()
        Config.test_mistral_connection()
        print("\n🎉 All configuration checks passed!")
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        print("\n💡 Make sure you have a .env file with your API keys")