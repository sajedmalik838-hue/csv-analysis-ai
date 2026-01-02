import sys
import os

with open('diagnostics.txt', 'w') as f:
    f.write(f"Python Version: {sys.version}\n")
    f.write(f"CWD: {os.getcwd()}\n")
    try:
        import streamlit
        f.write(f"Streamlit Version: {streamlit.__version__}\n")
    except Exception as e:
        f.write(f"Streamlit Import Error: {str(e)}\n")
    
    try:
        import pandas as pd
        f.write(f"Pandas Version: {pd.__version__}\n")
    except Exception as e:
        f.write(f"Pandas Import Error: {str(e)}\n")

    try:
        import google.generativeai as genai
        f.write("Gemini SDK imported successfully\n")
    except Exception as e:
        f.write(f"Gemini Import Error: {str(e)}\n")

f.close()
