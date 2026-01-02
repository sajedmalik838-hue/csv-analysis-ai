import streamlit as st
import pandas as pd
import io
import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="csv-analysis-ai",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    """Get Gemini client with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found. Please set it in Streamlit Cloud secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

def get_csv_summary(df):
    """Generate comprehensive summary of the dataframe"""
    summary = f"""
CSV DATA CONTEXT:

DATASET OVERVIEW:
- Total Rows: {len(df):,}
- Total Columns: {len(df.columns)}
- Column Names: {', '.join(df.columns.tolist())}

COLUMN DETAILS:
"""
    
    # Add column information
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        missing_count = df[col].isnull().sum()
        summary += f"- {col}: {dtype} | Unique: {unique_count} | Missing: {missing_count}\n"
    
    # Add sample data
    summary += f"""
SAMPLE DATA (First 3 rows):
{df.head(3).to_string()}

STATISTICAL SUMMARY:
"""
    
    # Add numeric statistics if available
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        summary += df[numeric_cols].describe().to_string()
    else:
        summary += "No numeric columns for statistical summary"
    
    return summary

def get_ai_response(question, df):
    """Get response from Gemini AI about the CSV data"""
    try:
        client = get_gemini_client()
        data_summary = get_csv_summary(df)
        
        prompt = f"""
You are a data analyst assistant. Below is CSV data:

{data_summary}

USER QUESTION: {question}

IMPORTANT INSTRUCTIONS:
1. Answer based ONLY on the data provided above
2. Be specific - include actual numbers, values, and column names
3. If calculation is needed, show your reasoning
4. If the data doesn't contain the answer, say so clearly
5. Format your answer clearly with bullet points or paragraphs

ANSWER:
"""
        
        response = client.models.generate_content(
            model=st.session_state.get("model", "gemini-2.5-flash"),
            contents=prompt
        )
        
        return response.text
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Main App
st.title("🤖 AI CSV Chatbot")
st.markdown("Upload a CSV file and chat with AI about your data")

# Sidebar
with st.sidebar:
    st.header("📁 Upload CSV File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        # Check if this is a new file
        if st.session_state.file_name != uploaded_file.name:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.file_name = uploaded_file.name
                st.session_state.messages = []  # Clear previous chat
                
                st.success(f"✅ Loaded: {uploaded_file.name}")
                
                # Display statistics
                st.subheader("📊 Data Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                
                # Show memory usage
                mem_usage = df.memory_usage(deep=True).sum() / 1024
                st.caption(f"Memory: {mem_usage:.1f} KB")
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    # Model selection
    st.divider()
    st.header("⚙️ Settings")
    
    model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    st.session_state.model = st.selectbox(
        "Select Gemini Model",
        model_options,
        index=0
    )
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Powered by Google Gemini AI")

# Main content area
if st.session_state.df is not None:
    # Display chat messages
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
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt, st.session_state.df)
                st.markdown(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Data preview tabs
    tab1, tab2 = st.tabs(["📋 Data Preview", "📈 Statistics"])
    
    with tab1:
        st.dataframe(st.session_state.df, use_container_width=True, height=500)
    
    with tab2:
        df = st.session_state.df
        # Numeric statistics
        if not df.select_dtypes(include=['number']).empty:
            st.subheader("Numeric Columns Statistics")
            st.dataframe(df.describe(), use_container_width=True)
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            st.subheader("Missing Values")
            st.dataframe(missing[missing > 0].rename("Missing Count"), use_container_width=True)
        else:
            st.info("✅ No missing values found")

else:
    # Welcome screen
    st.info("👈 Upload a CSV file from the sidebar to start!")
    
    st.markdown("""
    ### ✨ Features:
    - 📁 **Upload any CSV file**
    - 💬 **Ask natural language questions**
    - 🤖 **Powered by Google Gemini AI**
    - 📊 **Automatic data analysis**
    
    ### 📝 Example Questions:
    - "What columns are in my data?"
    - "Show me the first 5 rows"
    - "What's the average of [column name]?"
    - "How many missing values are there?"
    - "Find rows where [condition]"
    
    ### ⚠️ Note:
    - Files are processed locally in your browser
    - No data is stored on our servers
    - Supports files up to 200MB
    """)

# Footer
st.divider()
st.caption("Built with Streamlit & Google Gemini AI | Files are processed locally")