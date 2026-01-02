from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("Listing models using new google-genai SDK:")
try:
    for model in client.models.list():
        print(f"Name: {model.name}")
        print(f"Capabilities: {model.supported_actions}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
