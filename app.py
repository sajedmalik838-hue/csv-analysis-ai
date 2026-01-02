import streamlit as st
import pandas as pd
import requests
import io

# Page configuration
st.set_page_config(
    page_title="AI Chatbot Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://127.0.0.1:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "csv_data" not in st.session_state:
    st.session_state.csv_data = None
if "csv_name" not in st.session_state:
    st.session_state.csv_name = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None

def upload_to_api(file_obj):
    """Upload CSV to FastAPI backend"""
    try:
        # Reset file pointer to beginning before sending
        file_obj.seek(0)
        files = {"file": (file_obj.name, file_obj, "text/csv")}
        response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            return response.json().get("session_id")
        else:
            st.error(f"❌ API Upload Failed: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to backend. Is 'run_api.bat' running?")
        return None
    except Exception as e:
        st.error(f"❌ Error uploading file: {e}")
        return None

def chat_with_api(message, session_id):
    """Send message to FastAPI backend"""
    try:
        payload = {
            "session_id": session_id,
            "message": message,
            "model": st.session_state.get("current_model", "gemini-2.5-flash")
        }
        response = requests.post(f"{API_URL}/chat", json=payload)
        
        if response.status_code == 200:
            return response.json().get("response")
        elif response.status_code == 404:
             return "⚠️ Session expired or invalid. Please re-upload your CSV."
        elif response.status_code == 429:
             return "⚠️ API Quota Exceeded. Please try again later."
        else:
            return f"❌ API Error: {response.text}"
    except Exception as e:
        return f"❌ Connection Error: {e}"

# Main App
st.title("🤖 AI Chatbot Dashboard")
st.markdown("Upload a CSV file and chat with AI about your data (Powered by FastAPI)!")

# Sidebar for CSV upload and info
with st.sidebar:
    st.header("📁 Upload CSV File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        # Check if this is a new file or same file
        if st.session_state.csv_name != uploaded_file.name:
            # Read locally for specific preview
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.csv_data = df
                st.session_state.csv_name = uploaded_file.name
                
                # Upload to API
                with st.spinner("Uploading to AI Backend..."):
                    session_id = upload_to_api(uploaded_file)
                    if session_id:
                        st.session_state.session_id = session_id
                        st.success(f"✅ Loaded & Synced: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    if st.session_state.csv_data is not None:
        # Display statistics
        df = st.session_state.csv_data
        st.subheader("📊 Data Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", len(df))
            st.metric("Columns", len(df.columns))
        with col2:
             st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # Clear conversation button
    st.divider()
    st.header("⚙️ Settings")
    
    # Model selection (Pass this to API)
    model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    st.session_state.current_model = st.selectbox(
        "Select Gemini Model", model_options, index=0
    )

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content area
if st.session_state.csv_data is not None:
    # Create tabs for data view and chat
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Data Preview"])
    
    with tab1:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    with tab2:
        st.subheader(f"📄 {st.session_state.csv_name}")
        st.dataframe(st.session_state.csv_data, use_container_width=True, height=500)
        st.subheader("📈 Statistical Summary")
        st.dataframe(st.session_state.csv_data.describe(), use_container_width=True)

    # Chat input
    if prompt := st.chat_input("Ask me anything about your data..."):
        if not st.session_state.session_id:
            st.error("⚠️ Backend session missing. Please upload the file again.")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get API response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_with_api(prompt, st.session_state.session_id)
                    st.markdown(response)
                    
            st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("👈 Upload a CSV file to start!")
