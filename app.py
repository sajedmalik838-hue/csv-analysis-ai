import streamlit as st
import pandas as pd
import os
from google import genai

# Page configuration
st.set_page_config(page_title="AI CSV Chatbot", page_icon="🤖", layout="wide")

# Get Gemini client
@st.cache_resource
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not set. Please add it in Streamlit Cloud secrets.")
        st.stop()
    return genai.Client(api_key=api_key)

# Session state
if 'df' not in st.session_state:
    st.session_state.df = None

st.title("🤖 AI CSV Chatbot")
st.markdown("Upload a CSV file and chat with AI")

# File upload
uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    
    st.success(f"✅ Loaded: {uploaded_file.name}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    
    # Ask question
    question = st.text_input("Ask about your data:")
    
    if question and st.button("Get Answer"):
        with st.spinner("Analyzing..."):
            try:
                client = get_client()
                
                # Create prompt
                prompt = f"""
CSV Data:
- File: {uploaded_file.name}
- Rows: {len(df)}, Columns: {len(df.columns)}
- Columns: {', '.join(df.columns.tolist())}
- Sample data (first 3 rows):
{df.head(3).to_string()}

Question: {question}

Answer based on the data:
"""
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                st.success("🤖 AI Response:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Show data
    with st.expander("📋 View Data"):
        st.dataframe(df)

else:
    st.info("👈 Upload a CSV file to start!")