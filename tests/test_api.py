import requests
import os

# Configuration
API_URL = "http://127.0.0.1:8000"
SAMPLE_CSV = "sample_data.csv"

def test_api():
    print("🧪 Testing Gemini CSV Chat API...")
    
    # 1. Test Root
    try:
        resp = requests.get(f"{API_URL}/")
        print(f"ROOT: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"❌ Failed to connect to API. Is it running? Error: {e}")
        return

    # 2. Upload File
    print("\n📤 Uploading sample_data.csv...")
    if not os.path.exists(SAMPLE_CSV):
        print(f"❌ Error: {SAMPLE_CSV} not found. Please ensure it exists.")
        return

    with open(SAMPLE_CSV, "rb") as f:
        files = {"file": (SAMPLE_CSV, f, "text/csv")}
        resp = requests.post(f"{API_URL}/upload", files=files)
    
    if resp.status_code != 200:
        print(f"❌ Upload Failed: {resp.text}")
        return
    
    upload_data = resp.json()
    session_id = upload_data.get("session_id")
    print(f"✅ Upload Success! Session ID: {session_id}")
    print(f"   Data: {upload_data}")

    # 3. Chat
    print("\n💬 Testing Chat...")
    chat_payload = {
        "session_id": session_id,
        "message": "How many rows are there?",
        "model": "gemini-2.5-flash"
    }
    
    resp = requests.post(f"{API_URL}/chat", json=chat_payload)
    
    if resp.status_code == 200:
        print(f"✅ Chat Response: {resp.json()['response']}")
    else:
        print(f"❌ Chat Failed: {resp.text}")

if __name__ == "__main__":
    test_api()
