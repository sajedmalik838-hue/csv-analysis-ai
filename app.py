import streamlit as st
import pandas as pd
import os
from google import genai

# ========== CONFIGURATION ==========
st.set_page_config(
    page_title="AI CSV Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ========== GEMINI CLIENT ==========
@st.cache_resource
def get_gemini_client():
    """Initialize Gemini AI client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("""
        ❌ GEMINI_API_KEY not found!
        
        Please add it in Streamlit Cloud:
        1. Go to app settings (⚙️)
        2. Click "Secrets"
        3. Add: GEMINI_API_KEY = "your_key_here"
        4. Click "Save" then "Rerun"
        """)
        st.stop()
    return genai.Client(api_key=api_key)

# ========== SESSION STATE ==========
if 'df' not in st.session_state:
    st.session_state.df = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ========== MAIN APP ==========
st.title("🤖 AI CSV Chatbot")
st.markdown("---")

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("📁 Upload CSV")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your CSV data file"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            st.session_state.messages = []  # Clear chat
            
            st.success(f"✅ **{uploaded_file.name}**")
            
            # Quick stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
                
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.divider()
    
    if st.button("🔄 Clear & Restart", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ========== MAIN CONTENT ==========
if st.session_state.df is not None:
    df = st.session_state.df
    
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
            with st.spinner("🤔 Analyzing your data..."):
                try:
                    client = get_gemini_client()
                    
                    # Create data context
                    context = f"""
## CSV DATA ANALYSIS

**File:** {st.session_state.file_name}
**Rows:** {len(df):,} | **Columns:** {len(df.columns)}

**COLUMNS:**
{', '.join(df.columns.tolist())}

**SAMPLE DATA (First 3 rows):**
{df.head(3).to_string()}

**USER QUESTION:** {prompt}

**INSTRUCTIONS:** Answer based ONLY on the data above. Be specific and include numbers/values when possible.
"""
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=context
                    )
                    
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"""
                    ❌ **Error:** {str(e)}
                    
                    **Possible fixes:**
                    1. Check if GEMINI_API_KEY is set in Streamlit Cloud secrets
                    2. Verify your API key is valid
                    3. Try again in a few moments
                    """
                    st.error(error_msg)
    
    # Data preview tabs
    tab1, tab2 = st.tabs(["📋 Data Preview", "📊 Statistics"])
    
    with tab1:
        st.dataframe(df, use_container_width=True, height=400)
    
    with tab2:
        if not df.select_dtypes(include=['number']).empty:
            st.dataframe(df.describe(), use_container_width=True)
        else:
            st.info("📝 No numeric columns for statistical summary")
        
        # Column info
        st.subheader("📝 Column Information")
        for col in df.columns:
            unique_count = df[col].nunique()
            missing_count = df[col].isnull().sum()
            st.write(f"**{col}:** {df[col].dtype} | Unique: {unique_count} | Missing: {missing_count}")

else:
    # Welcome screen
    st.info("👈 **Upload a CSV file from the sidebar to begin!**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ **Features**
        - 📁 Upload any CSV file
        - 💬 Ask questions in plain English
        - 🤖 AI-powered analysis
        - 📊 Instant data preview
        - 🔍 Statistical insights
        """)
    
    with col2:
        st.markdown("""
        ### 💡 **Example Questions**
        - _"What columns are in my data?"_
        - _"Show me the first 5 rows"_
        - _"What's the average of [column]?"_
        - _"How many missing values?"_
        - _"Find rows where [condition]"_
        """)
    
    st.divider()
    st.markdown("""
    ### 🚀 **Quick Start**
    1. **Upload** your CSV file
    2. **Ask** a question about your data
    3. **Get** instant AI-powered answers
    """)

# ========== FOOTER ==========
st.markdown("---")
st.caption("""
🔒 **Privacy:** Your data is processed locally and not stored | 
🤖 **Powered by Google Gemini AI** | 
🚀 **Built with Streamlit**
""")