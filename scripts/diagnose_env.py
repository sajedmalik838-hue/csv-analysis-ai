import sys
import os
import subprocess

def check():
    print(f"Python: {sys.version}")
    print(f"CWD: {os.getcwd()}")
    
    modules = ['streamlit', 'pandas', 'google.generativeai', 'dotenv']
    for mod in modules:
        try:
            __import__(mod)
            print(f"Module {mod}: INSTALLED")
        except ImportError:
            print(f"Module {mod}: MISSING")
            
    try:
        result = subprocess.run(['streamlit', '--version'], capture_output=True, text=True)
        print(f"Streamlit CLI: {result.stdout.strip()}")
    except Exception as e:
        print(f"Streamlit CLI Error: {e}")

if __name__ == "__main__":
    check()
