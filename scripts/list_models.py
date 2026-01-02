import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    # Print first and last 4 chars for verification without exposing secret
    print(f"API Key prefix/suffix: {api_key[:4]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

print("\n--- Available Models ---")
try:
    models = genai.list_models()
    for m in models:
        print(f"Name: {m.name}")
        print(f"Supported methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models: {str(e)}")
