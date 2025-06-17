import streamlit as st
import requests
import uuid
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import html

# Load environment variables
load_dotenv()

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
    """Initialize session state variables"""
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
            padding: 12px 20px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(70, 130, 180, 0.4);
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            min-width: 50px;
            height: 50px;
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
                    <h3>🚀 Welcome to Orbitx IWO!</h3>
                    <p>Start your conversation with our AI agents. They can help with HR, CRM, IT, Marketing, Sales, and Analytics.</p>
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
    # Page config
    st.set_page_config(
        page_title="Orbitx IWO",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session
    initialize_session()
    
    # Apply custom styling
    apply_custom_css()
    
    # Main container
    with st.container():
        # Header
        st.markdown('<h1 class="main-header">💫 Orbitx IWO</h1>', unsafe_allow_html=True)
        
        # Display chat history
        display_chat_history()
        
        # Input area - Simple layout with visible buttons
        # ✅ FIXED INPUT AREA (replace your old input+buttons block with this)

# Proper text input with a safe label to avoid warning
    # ✅ FIXED INPUT & BUTTONS — drop this inside `main()`

        # ✅ FINAL FIXED BLOCK — working SEND

        col1, col2, col3 = st.columns([10, 1, 1])

        with col1:
            text_input = st.text_area(
                "User Input",
                value=st.session_state.get('speech_text', ''),
                placeholder="Type your message here...",
                label_visibility="collapsed"
            )

        with col2:
            mic_label = "🔴" if st.session_state.get('is_recording', False) else "🎤"
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
        st.write(f"**Session ID:** `{st.session_state.session_id}`")
        st.write(f"**Messages:** {len(st.session_state.chat_history)}")
        st.write(f"**Loading:** {st.session_state.is_loading}")
        st.write(f"**Recording:** {st.session_state.is_recording}")
        st.write(f"**N8N URL:** {N8N_WEBHOOK_URL}")
        
        # Show recent errors or logs
        st.subheader("Recent Activity Log")
        if st.session_state.chat_history:
            for i, msg in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 messages
                st.write(f"**{i+1}.** [{msg['timestamp']}] {msg['role']}: {msg['content'][:100]}...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("Reset Session"):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                st.session_state.speech_text = ""
                st.session_state.is_recording = False
                st.rerun()
        
        with col3:
            if st.button("Test Connection"):
                st.write("Testing connection...")
                test_response = send_message_to_n8n(st.session_state.session_id, "test")
                st.write(f"Test result: {test_response}")
    
    # Footer
    st.markdown('<div class="footer">© 2025 Orbitx</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()