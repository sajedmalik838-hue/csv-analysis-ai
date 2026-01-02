import streamlit as st
import pandas as pd
import os
from google import genai

# Page configuration
st.set_page_config(
    page_title="AI CSV Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not set. Please add it in Streamlit Cloud secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# Session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("🤖 AI CSV Chatbot")
st.markdown("Upload a CSV file and chat with AI about your data")

# Sidebar
with st.sidebar:
    st.header("📁 Upload CSV")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv']
    )
    
    if uploaded_file:
        if st.session_state.file_name != uploaded_file.name:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.file_name = uploaded_file.name
                st.session_state.messages = []  # Clear chat
                st.success(f"✅ Loaded: {uploaded_file.name}")
                
                # Show stats
                st.subheader("📊 Data Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                    
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main area
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Display chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(f"Ask about {st.session_state.file_name}..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    client = get_gemini_client()
                    
                    # Create data context
                    context = f"""
CSV Data:
- File: {st.session_state.file_name}
- Rows: {len(df)}, Columns: {len(df.columns)}
- Column names: {', '.join(df.columns.tolist())}
- First 3 rows:
{df.head(3).to_string()}

User Question: {prompt}

Please answer based only on the data above. Be specific and include numbers when possible.
"""
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=context
                    )
                    
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
    
    # Data preview
    with st.expander("📋 View Data"):
        st.dataframe(df, use_container_width=True, height=300)
    
    with st.expander("📊 Statistics"):
        if not df.select_dtypes(include=['number']).empty:
            st.dataframe(df.describe())
        else:
            st.info("No numeric columns")

else:
    # Welcome message
    st.info("👈 Upload a CSV file from the sidebar to start!")
    
    st.markdown("""
    ### 🚀 How to use:
    1. **Upload** a CSV file
    2. **Ask questions** about your data
    3. **Get AI-powered answers**
    
    ### 💡 Example questions:
    - "What columns are in my data?"
    - "Show me the first 5 rows"
    - "What's the average of column X?"
    - "How many missing values?"
    - "Find rows where condition"
    """)

# Footer
st.divider()
st.caption("Built with Streamlit & Google Gemini AI")