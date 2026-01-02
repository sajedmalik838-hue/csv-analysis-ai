import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print(f"Testing gemini-2.0-flash-exp...")
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Hello, are you there?")
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error with gemini-2.0-flash-exp: {str(e)}")
