import streamlit as st
import requests
import uuid
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import html

import json
from pathlib import Path
import time

from config import Config
from updated_workflow_agent_mistral import WorkflowGeneratorAgent

# Page config
st.set_page_config(
    page_title="Orbitx IWO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
    )
    
# Load environment variables
load_dotenv()

# Initialize Workflow Agent
try:
    Config.validate_config()
    workflow_agent = WorkflowGeneratorAgent(
        mistral_api_key=Config.MISTRAL_API_KEY,
        n8n_base_url=Config.N8N_BASE_URL,
        n8n_api_key=Config.N8N_API_KEY,
        chroma_host=Config.CHROMA_HOST,
        chroma_port=Config.CHROMA_PORT
    )
    st.success("⭐ Star Agent(Workflow Generator) initialized successfully!")
except Exception as e:
    workflow_agent = None
    st.warning(f"⚠️ Workflow Agent not available: {str(e)[:50]}...")

# Configuration
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')

# Add this after load_dotenv()
if not N8N_WEBHOOK_URL:
    st.error("❌ N8N_WEBHOOK_URL not found in environment variables")
    st.stop()

if not N8N_WEBHOOK_URL.startswith(('http://', 'https://')):
    st.error(f"❌ Invalid URL format: {N8N_WEBHOOK_URL}. URL must start with http:// or https://")
    st.stop()

API_TIMEOUT = 30  # seconds

def initialize_session():
    """Initialize session state variables with workflow management"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_loading' not in st.session_state:
        st.session_state.is_loading = False
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'speech_text' not in st.session_state:
        st.session_state.speech_text = ""
    
    # NEW - Workflow state management
    if 'last_generated_workflow' not in st.session_state:
        st.session_state.last_generated_workflow = None
    if 'last_deployed_workflow_id' not in st.session_state:
        st.session_state.last_deployed_workflow_id = None
    if 'workflow_generation_history' not in st.session_state:
        st.session_state.workflow_generation_history = []

def apply_custom_css():
    """Apply custom CSS styling for space theme"""
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');
        
        /* Main App Background - Added more black */
        .stApp {
            background: linear-gradient(135deg, 
                #050a1a 0%, 
                #0a1228 25%, 
                #0c1530 50%, 
                #0f1422 75%, 
                #0a1228 100%);
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }
        
        /* Animated Stars Background */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                radial-gradient(2px 2px at 20px 30px, #ffffff, transparent),
                radial-gradient(2px 2px at 40px 70px, #87ceeb, transparent),
                radial-gradient(1px 1px at 90px 40px, #ffffff, transparent),
                radial-gradient(1px 1px at 130px 80px, #87ceeb, transparent),
                radial-gradient(2px 2px at 160px 120px, #ffffff, transparent),
                radial-gradient(1px 1px at 200px 50px, #b0e0e6, transparent),
                radial-gradient(2px 2px at 240px 90px, #ffffff, transparent),
                radial-gradient(1px 1px at 280px 30px, #87ceeb, transparent),
                radial-gradient(1px 1px at 320px 110px, #ffffff, transparent),
                radial-gradient(2px 2px at 360px 60px, #b0e0e6, transparent),
                radial-gradient(1px 1px at 400px 20px, #ffffff, transparent),
                radial-gradient(1px 1px at 440px 100px, #87ceeb, transparent),
                radial-gradient(2px 2px at 480px 140px, #ffffff, transparent),
                radial-gradient(1px 1px at 520px 45px, #b0e0e6, transparent),
                radial-gradient(1px 1px at 560px 85px, #ffffff, transparent),
                radial-gradient(2px 2px at 600px 25px, #87ceeb, transparent);
            background-repeat: repeat;
            background-size: 650px 650px;
            animation: twinkle 4s ease-in-out infinite alternate;
            z-index: 0;
            opacity: 0.7;
        }
        
        /* Gradient Overlay */
        .stApp::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(ellipse at top, rgba(135, 206, 235, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at bottom, rgba(176, 224, 230, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at center, rgba(70, 130, 180, 0.04) 0%, transparent 70%);
            z-index: 1;
            pointer-events: none;
        }
        
        /* Animation for stars */
        @keyframes twinkle {
            0% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 0.9; transform: scale(1.1); }
            100% { opacity: 0.7; transform: scale(1); }
        }
        
        /* Ensure content is above background */
        .main .block-container {
            position: relative;
            z-index: 2;
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Header Styling - Enhanced */
        .main-header {
            text-align: center;
            color: #ffffff;
            font-size: 3.5rem;
            font-weight: 900;
            font-family: 'Orbitron', monospace;
            margin-bottom: 2rem;
            text-shadow: 
                0 0 20px rgba(135, 206, 235, 0.8),
                0 0 40px rgba(135, 206, 235, 0.4),
                0 0 60px rgba(135, 206, 235, 0.2);
            letter-spacing: 3px;
            background: linear-gradient(45deg, #87ceeb, #ffffff, #87ceeb);
            background-size: 200% 200%;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Chat Container */
        .chat-container {
            background: rgba(10, 18, 40, 0.6);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            border: 1px solid rgba(135, 206, 235, 0.2);
            backdrop-filter: blur(15px);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            min-height: 400px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        /* Welcome Message */
        .welcome-message {
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            padding: 3rem 2rem;
            font-family: 'Inter', sans-serif;
        }
        
        .welcome-message h3 {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #87ceeb;
            font-family: 'Orbitron', monospace;
        }
        
        .welcome-message p {
            font-size: 1.1rem;
            line-height: 1.6;
            opacity: 0.8;
        }
        
        /* Message Bubbles */
        .user-message {
            background: linear-gradient(135deg, #4682b4, #5f9ea0);
            color: white;
            padding: 15px 20px;
            border-radius: 20px 20px 5px 20px;
            margin: 15px 0 15px 15%;
            box-shadow: 0 4px 15px rgba(70, 130, 180, 0.4);
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            line-height: 1.4;
            word-wrap: break-word;
            animation: slideInRight 0.3s ease-out;
        }
        
        .bot-message {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            padding: 15px 20px;
            border-radius: 20px 20px 20px 5px;
            margin: 15px 15% 15px 0;
            border: 1px solid rgba(135, 206, 235, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            line-height: 1.4;
            word-wrap: break-word;
            animation: slideInLeft 0.3s ease-out;
        }
        
        .message-timestamp {
            font-size: 0.75rem;
            opacity: 0.6;
            margin-top: 8px;
            font-weight: 300;
        }
        
        /* Message Animations */
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Input Area Container - Centered like debug info */
        .input-container {
            background: rgba(15, 27, 60, 0.3);
            border: 1px solid rgba(135, 206, 235, 0.2);
            border-radius: 20px;
            padding: 20px;
            margin: 20px auto;
            max-width: 1000px;
            display: flex;
            align-items: center;
            gap: 15px;
            backdrop-filter: blur(10px);
        }
        
        /* Input Area Styling - Better sizing and layout */
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #1a1a1a !important;
            border: 2px solid rgba(135, 206, 235, 0.4);
            border-radius: 15px;
            padding: 15px 20px;
            font-size: 16px;
            font-family: 'Inter', sans-serif;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            resize: none !important;
            height: 70px !important;
            min-height: 70px !important;
            width: 100% !important;
        }
        
        /* Button Container */
        .button-container {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-shrink: 0;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #4682b4, #5f9ea0);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 12px 45px;
            font-size: 50px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(70, 130, 180, 0.4);
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            min-width: 80px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 !important;
        }

        /* Text input container sizing */
        .stTextArea {
            flex: 1;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Loading Animation */
        .loading-container {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #87ceeb;
            font-family: 'Inter', sans-serif;
        }
        
        .loading-dots {
            display: inline-flex;
            gap: 4px;
        }
        
        .loading-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #87ceeb;
            animation: loading 1.4s ease-in-out infinite both;
        }
        
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        .loading-dots span:nth-child(3) { animation-delay: 0s; }
        
        @keyframes loading {
            0%, 80%, 100% { 
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% { 
                transform: scale(1.2);
                opacity: 1;
            }
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.5);
            font-size: 14px;
            font-family: 'Inter', sans-serif;
            margin-top: 2rem;
            padding: 1rem;
        }
        
        /* Scrollbar Styling */
        .chat-container::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-container::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb {
            background: rgba(135, 206, 235, 0.5);
            border-radius: 10px;
        }
        
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: rgba(135, 206, 235, 0.7);
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        .stDeployButton {display: none;}
        footer {visibility: hidden;}
        .stApp > header {visibility: hidden;}
        
        /* Debug panel styling */
        .stExpander {
            background: rgba(15, 27, 60, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(135, 206, 235, 0.2);
        }
        
        /* Error message styling */
        .error-message {
            background: rgba(220, 53, 69, 0.2);
            border: 1px solid rgba(220, 53, 69, 0.5);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            color: #ff6b7a;
            font-family: 'Inter', sans-serif;
        }

        .voice-interface {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def send_message_to_n8n(session_id, message):
    """Send message to n8n webhook and get response"""
    try:
        payload = {
            "sessionId": session_id,
            "message": message
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add debug logging
        st.write(f"🔍 DEBUG: Sending to {N8N_WEBHOOK_URL}")
        st.write(f"🔍 DEBUG: Payload: {payload}")
        
        response = requests.post(
            N8N_WEBHOOK_URL, 
            json=payload, 
            headers=headers, 
            timeout=API_TIMEOUT
        )
        
        st.write(f"🔍 DEBUG: Response Status: {response.status_code}")
        st.write(f"🔍 DEBUG: Response Text: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "message": f"Failed to get response from AI agent. Response: {response.text}"
            }
    
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. Please try again."
        st.error(f"⏱️ TIMEOUT ERROR: {error_msg}")
        return {
            "error": "Timeout",
            "message": error_msg
        }
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Unable to connect to AI service. Connection Error: {str(e)}"
        st.error(f"🔌 CONNECTION ERROR: {error_msg}")
        return {
            "error": "Connection Error",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        st.error(f"❌ UNEXPECTED ERROR: {error_msg}")
        return {
            "error": "Unexpected Error",
            "message": error_msg
        }

def display_chat_history():
    """Display the chat history with proper styling"""
    if not st.session_state.chat_history:
        st.markdown('''                        
        <div class="chat-container">
            <div class="welcome-message">
                <h3>☀️ Sun Agent </h3>
                <h4>Your AI copilots for HR, CRM, IT, Marketing, Sales & Analytics - Chat with Orbitx 🤖</h4>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Use container for better styling
        with st.container():
            for message in st.session_state.chat_history:
                timestamp = message.get('timestamp', '')
                content = str(message['content'])
                    
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong> {content}
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Clean the content for display
                    clean_content = content.replace('&quot;', '"').replace('&amp;', '&')
                    st.markdown(f"""
                    <div class="bot-message">
                        <strong>🤖 Orbitx Agent:</strong> {clean_content}
                        <div class="message-timestamp">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
def add_message_to_history(role, content):
    """Add a message to chat history with timestamp"""
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        'role': role,
        'content': str(content),  # Ensure content is string
        'timestamp': timestamp
    })

def process_message(message):
    """Process user message and get response"""
    add_message_to_history("user", message)
    st.session_state.is_loading = True
    
    # Get AI response
    response = send_message_to_n8n(
        st.session_state.session_id, 
        message
    )
    
    # Process response
    if 'error' in response:
        ai_message = f"❌ {response['message']}"
    else:
        # Extract message from response (adjust based on your n8n response format)
        ai_message = response.get('message', response.get('response', str(response)))
    
    # Add AI response to history
    add_message_to_history('assistant', ai_message)
    
    # Clear loading state
    st.session_state.is_loading = False

def main():
    """Main application function"""

    # Initialize session
    initialize_session()
    
    # Apply custom styling
    apply_custom_css()
    
    # Main container
    with st.container():
        # Header
        st.markdown('<h1 class="main-header">Welcome to Orbitx IWO</h1>', unsafe_allow_html=True)
        
        # Display chat history
        display_chat_history()
        
        # Input area - Simple layout with visible buttons
        # ✅ FIXED INPUT AREA (replace your old input+buttons block with this)

# Proper text input with a safe label to avoid warning
    # ✅ FIXED INPUT & BUTTONS — drop this inside `main()`

        # ✅ FINAL FIXED BLOCK — working SEND

        col1, col2, col3 = st.columns([10, 0.85, 1])

        with col1:
            text_input = st.text_area(
                "User Input",
                value=st.session_state.get('speech_text', ''),
                placeholder="Type your message here...",
                label_visibility="collapsed"
            )

        with col2:
            mic_label = "🟥" if st.session_state.get('is_recording', False) else "🎙️"
            if st.button(mic_label, key="mic_button"):
                st.session_state.is_recording = not st.session_state.get('is_recording', False)
                st.rerun()

        with col3:
            send_disabled = not bool(text_input and text_input.strip())
            if st.button("SEND", key="send_button"):
                if text_input.strip():
                    process_message(text_input.strip())
                    st.session_state.speech_text = ""
                    st.rerun()




        # Voice recording interface
        if st.session_state.get('is_recording', False):
            st.markdown('<div class="voice-interface">', unsafe_allow_html=True)
            st.components.v1.html("""
                <div style="padding: 10px; text-align: center; color: white;">
                    <div id="result">Listening...</div>
                </div>
                <script>
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-US';
                recognition.continuous = false;
                recognition.interimResults = false;

                recognition.onstart = () => {
                    document.getElementById('result').innerHTML = '🎤 Listening...';
                };

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('result').innerHTML = '✅ ' + transcript;
                    
                    // Update textarea
                    const textarea = document.querySelector('textarea');
                    if (textarea) {
                        textarea.value = transcript;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                };

                recognition.start();
                </script>
            """, height=100)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Debug section - Always show for debugging errors
    with st.expander("🔧 Debug Info & Error Logs", expanded=False):
    # Basic session info
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Session Info:**")
            st.write(f"Session ID: `{st.session_state.session_id[:8]}...`")
            st.write(f"Messages: {len(st.session_state.chat_history)}")
            st.write(f"Loading: {st.session_state.is_loading}")
            st.write(f"Recording: {st.session_state.is_recording}")
        
        with col2:
            st.write("**Workflow Status:**")
            
            # Detailed workflow status
            if st.session_state.last_generated_workflow:
                workflow_name = st.session_state.last_generated_workflow.get('name', 'Unknown')
                node_count = len(st.session_state.last_generated_workflow.get('nodes', []))
                st.write(f"✅ Generated: {workflow_name}")
                st.write(f"📊 Nodes: {node_count}")
            else:
                st.write("❌ No workflow generated")
                
            if st.session_state.last_deployed_workflow_id:
                st.write(f"🚀 Deployed: `{st.session_state.last_deployed_workflow_id}`")
            else:
                st.write("⏳ Not deployed")
        
        # Connection status
        st.write("**Connection Status:**")
        connection_col1, connection_col2 = st.columns(2)
        
        with connection_col1:
            st.write(f"N8N URL: `{Config.N8N_BASE_URL}`")
            if workflow_agent:
                st.write("✅ Workflow Agent: Active")
            else:
                st.write("❌ Workflow Agent: Inactive")
        
        with connection_col2:
            st.write(f"Webhook: `{N8N_WEBHOOK_URL[:30]}...`")
            # Test ChromaDB connection
            try:
                if workflow_agent and hasattr(workflow_agent, 'chroma_client'):
                    st.write("✅ ChromaDB: Connected")
                else:
                    st.write("⚠️ ChromaDB: Unknown")
            except:
                st.write("❌ ChromaDB: Error")
        
        # File system status
        st.write("**File System Status:**")
        workflows_dir = Path("generated_workflows")
        latest_file = workflows_dir / "latest_workflow.json"
        
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("workflow_*.json"))
            st.write(f"📁 Workflow files: {len(workflow_files)}")
            
            if latest_file.exists():
                try:
                    file_size = latest_file.stat().st_size
                    mod_time = latest_file.stat().st_mtime
                    st.write(f"📄 Latest workflow: {file_size} bytes, modified {datetime.fromtimestamp(mod_time).strftime('%H:%M:%S')}")
                except:
                    st.write("📄 Latest workflow: File exists but unreadable")
            else:
                st.write("📄 Latest workflow: Not found")
        else:
            st.write("📁 Workflows directory: Not created")
        
        # Recent activity log
        st.subheader("📋 Recent Activity Log")
        
        # Workflow activity
        if st.session_state.workflow_generation_history:
            st.write("**Workflow Generation History:**")
            for i, record in enumerate(st.session_state.workflow_generation_history[-3:]):
                time_str = record['timestamp'][11:19]  # Just time portion
                st.write(f"• [{time_str}] Generated '{record['workflow_name']}' ({record['node_count']} nodes)")
        
        # Chat activity
        if st.session_state.chat_history:
            st.write("**Recent Chat Messages:**")
            for i, msg in enumerate(st.session_state.chat_history[-3:]):
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                content_preview = str(msg['content'])[:60] + "..." if len(str(msg['content'])) > 60 else str(msg['content'])
                st.write(f"• [{msg['timestamp']}] {role_icon} {content_preview}")
        
        # Debug action buttons
        st.subheader("🛠️ Debug Actions")
        
        button_col1, button_col2, button_col3, button_col4 = st.columns(4)
        
        with button_col1:
            if st.button("🔄 Test Connection", key="test_conn"):
                st.write("Testing n8n connection...")
                test_response = send_message_to_n8n(st.session_state.session_id, "test connection")
                if 'error' in test_response:
                    st.error(f"❌ Connection failed: {test_response['message']}")
            else:
                st.success("✅ Connection successful!")

        with button_col2:
            if st.button("📂 Load Workflow", key="load_workflow"):
                if workflow_agent:
                    loaded = workflow_agent.load_latest_workflow()
                    if loaded:
                        st.session_state.last_generated_workflow = loaded
                        st.success("✅ Workflow loaded!")
                    else:
                        st.warning("⚠️ No workflow to load")

        with button_col3:
            if st.button("🧹 Clear Chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.success("Chat cleared!")
                st.rerun()

        with button_col4:
            if st.button("🔄 Reset All", key="reset_all"):
                # Reset session
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                st.session_state.speech_text = ""
                st.session_state.is_recording = False
                st.session_state.last_generated_workflow = None
                st.session_state.last_deployed_workflow_id = None
                st.session_state.workflow_generation_history = []
                
                # Reset agent
                if workflow_agent:
                    workflow_agent.last_generated_workflow = None
                
                st.success("🔄 Everything reset!")
                st.rerun()

    # Add clear workflow data button
    if st.button("Clear Workflow Data"):
        st.session_state.last_generated_workflow = None
        st.session_state.last_deployed_workflow_id = None
        st.session_state.workflow_generation_history = []
        if workflow_agent:
            workflow_agent.last_generated_workflow = None
        # Clean up files
        try:
            latest_file = Path("generated_workflows/latest_workflow.json")
            if latest_file.exists():
                latest_file.unlink()
        except:
            pass
        st.success("🧹 Workflow data cleared!")
        st.rerun()

    # Workflow Generator Agent Section (FIXED - No nested expanders)
    st.markdown("---")
    st.markdown("Workflow Generator")

    # Enhanced header with status
    st.markdown('''
    <div style="text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">⭐ Star Agent</h3>
        <h4 style="color: white; margin: 5px 0 0 0;">Your AI assistant to design, generate, and deploy workflows 🚀</h4>
    </div>
    ''', unsafe_allow_html=True)

    

    

    # Input section with examples
    col1, col2 = st.columns([4, 1.2])

    with col1:
        # Enhanced text area with examples
        agent_input = st.text_area(
            "Describe your workflow:",
            placeholder="Example: Create an employee onboarding workflow that collects info from BambooHR, sends Slack notifications, creates Google accounts, and assigns training tasks",
            key="agent_input",
            height=100,
            help="Be specific about the steps, integrations, and data flow you need"
        )
        
        # Handle example selection if it exists
        if 'agent_input_example' in st.session_state:
            agent_input = st.session_state.agent_input_example
            del st.session_state.agent_input_example

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        
        # Generate button with better styling
        generate_btn = st.button(
            "🚀 Generate Workflow", 
            key="generate_workflow", 
            type="primary",
            help="Generate a new workflow based on your description",
            use_container_width=True
        )
        
        # Deploy button right below
        if st.session_state.last_generated_workflow:
            deploy_btn = st.button(
                "📤 Deploy Workflow", 
                key="deploy_from_star_agent", 
                type="secondary",
                help="Deploy the generated workflow to n8n",
                use_container_width=True
            )


    # Enhanced generation process
    if generate_btn and agent_input.strip():
        # Show progress steps
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Analyzing request
                status_text.text("🔍 Analyzing your request...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                # Step 2: Generating workflow
                status_text.text("⚙️ Generating workflow structure...")
                progress_bar.progress(50)
                
                result = workflow_agent.process_request(agent_input.strip())
                progress_bar.progress(75)
                
                # Step 3: Saving workflow
                status_text.text("💾 Saving workflow...")
                
                if hasattr(workflow_agent, 'last_generated_workflow') and workflow_agent.last_generated_workflow:
                    # Store in session state
                    st.session_state.last_generated_workflow = workflow_agent.last_generated_workflow
                    
                    # Add to history
                    generation_record = {
                        'timestamp': datetime.now().isoformat(),
                        'input': agent_input.strip(),
                        'workflow_name': workflow_agent.last_generated_workflow.get('name', 'Unknown'),
                        'node_count': len(workflow_agent.last_generated_workflow.get('nodes', []))
                    }
                    st.session_state.workflow_generation_history.append(generation_record)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Workflow generated successfully!")
                    
                    # Show success details
                    workflow_name = workflow_agent.last_generated_workflow.get('name', 'Unknown')
                    node_count = len(workflow_agent.last_generated_workflow.get('nodes', []))
                    
                    # Clear progress and show success
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.balloons()  # Celebration animation
                    st.success(f"🎉 Generated: **{workflow_name}** with {node_count} nodes!")
                    
                    # Show workflow preview (FIXED - No expander)
                    st.markdown("### 👀 Workflow Preview")
                    with st.container():
                        nodes = workflow_agent.last_generated_workflow.get('nodes', [])
                        st.write(f"**Workflow:** {workflow_name}")
                        st.write(f"**Description:** {workflow_agent.last_generated_workflow.get('meta', {}).get('description', 'No description')}")
                        
                        # Show nodes in a nice format
                        st.write("**Workflow Steps:**")
                        for i, node in enumerate(nodes, 1):
                            node_name = node.get('name', f'Node {i}')
                            node_type = node.get('type', 'unknown').split('.')[-1]
                            parameters = node.get('parameters', {})
                            
                            # Create a nice node display
                            with st.container():
                                st.markdown(f"**{i}. {node_name}** `({node_type})`")
                                if parameters:
                                    # Show key parameters
                                    key_params = []
                                    for key, value in list(parameters.items())[:3]:  # Show first 3 params
                                        if isinstance(value, str) and len(value) < 50:
                                            key_params.append(f"{key}: {value}")
                                    if key_params:
                                        st.caption("   " + " | ".join(key_params))
                        
                        # Show connections
                        connections = workflow_agent.last_generated_workflow.get('connections', {})
                        if connections:
                            st.write("**Connections:**")
                            for source, targets in connections.items():
                                if targets and targets.get('main'):
                                    for target in targets['main']:
                                        target_node = target[0].get('node') if target and len(target) > 0 else 'Unknown'
                                        st.caption(f"   {source} → {target_node}")
                    
                    # Show next steps
                    st.info("✨ **Next Steps:** Click the '📤 Deploy Workflow' button above to deploy this workflow to your n8n instance!")
                
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("✅ Workflow has been generated and is ready for deployement")
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Generation failed: {str(e)}")
                st.code(f"Full error: {str(e)}")

    # Handle deploy button from Star Agent section
    if 'deploy_btn' in locals() and deploy_btn:
        with st.spinner("🚀 Deploying workflow..."):
            try:
                workflow_to_deploy = st.session_state.last_generated_workflow
                
                if workflow_to_deploy:
                    workflow_name = workflow_to_deploy.get('name', 'Unknown Workflow')
                    node_count = len(workflow_to_deploy.get('nodes', []))
                    
                    st.success(f"✅ Deploying: **{workflow_name}** ({node_count} nodes)")
                    
                    # Attempt deployment
                    deploy_result = workflow_agent._deploy_workflow(workflow_to_deploy)
                    
                    if deploy_result and isinstance(deploy_result, dict):
                        workflow_id = (
                            deploy_result.get('id') or 
                            deploy_result.get('workflow_id') or 
                            deploy_result.get('workflowId') or
                            deploy_result.get('data', {}).get('id') or
                            deploy_result.get('result', {}).get('id')
                        )
                        
                        # Success handling
                        st.success("🚀 Workflow deployed successfully!")
                        
                        if workflow_id:
                            st.info(f"📋 **Workflow ID:** `{workflow_id}`")
                            st.session_state.last_deployed_workflow_id = workflow_id
                            
                            # Show n8n link if available
                            n8n_url = Config.N8N_BASE_URL.rstrip('/')
                            workflow_url = f"{n8n_url}/workflow/{workflow_id}"
                            st.markdown(f"🔗 **View in n8n:** [{workflow_url}]({workflow_url})")
                        
                        # Show deployment details (FIXED - No expander)
                        st.markdown("### 📊 Deployment Details")
                        with st.container():
                            st.json(deploy_result)
                            
                    else:
                        st.error("❌ Deployment failed: Invalid response from n8n server")
                        st.code(f"Response: {deploy_result}")
                        
                else:
                    st.error("❌ No workflow found to deploy!")
                    st.markdown("""
                    **Please try:**
                    1. Generate a workflow first using the text area above
                    2. Wait for the "✅ Workflow generated!" message
                    3. Then click Deploy
                    """)
                    
            except AttributeError as e:
                st.error("❌ Deployment method not available")
                st.code(f"Error: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ Deployment failed: {str(e)}")
                st.code(f"Full error: {str(e)}")

    # Workflow generation history (FIXED - No expander)
    st.markdown("---")
    st.markdown("### 📈 Generation History")
    if st.session_state.workflow_generation_history:
        for i, record in enumerate(reversed(st.session_state.workflow_generation_history[-5:])):
            st.markdown(f"""
            **{i+1}.** {record['workflow_name']} ({record['node_count']} nodes)  
            *Generated:* {record['timestamp'][:19]}  
            *Input:* {record['input'][:100]}...
            """)
        
        # Clear history button
        if st.button("🧹 Clear History", key="clear_workflow_history"):
            st.session_state.workflow_generation_history = []
            st.success("History cleared!")
            st.rerun()
    else:
        st.info("No workflows generated yet")

    # Quick actions
    st.markdown("---")
    st.markdown("**⚡ Quick Actions:**")

    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        if st.button("🔄 Reload Workflow", key="reload_workflow_star", use_container_width=True):
            if workflow_agent:
                loaded = workflow_agent.load_latest_workflow()
                if loaded:
                    st.session_state.last_generated_workflow = loaded
                    st.success("✅ Workflow reloaded!")
                    st.rerun()
                else:
                    st.warning("⚠️ No workflow to reload")

    with action_col2:
        if st.button("📂 Save Workflow", key="save_workflow_star", use_container_width=True):
            if st.session_state.last_generated_workflow:
                # Force save workflow
                if workflow_agent:
                    workflow_agent._ensure_workflow_persistence()
                    st.success("✅ Workflow saved!")
                else:
                    st.warning("⚠️ Agent not available")
            else:
                st.warning("⚠️ No workflow to save")

    with action_col3:
        if st.button("📋 View JSON", key="view_json_star", use_container_width=True):
            if st.session_state.last_generated_workflow:
                st.json(st.session_state.last_generated_workflow)
            else:
                st.info("⚠️ No workflow to display")

    with action_col4:
        if st.button("🧹 Clear Data", key="clear_data_star", use_container_width=True):
            st.session_state.last_generated_workflow = None
            st.session_state.last_deployed_workflow_id = None
            if workflow_agent:
                workflow_agent.last_generated_workflow = None
            st.success("🧹 Data cleared!")
            st.rerun()

    

    # Footer
    st.markdown('<div class="footer">© 2025 Orbitx</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
                    