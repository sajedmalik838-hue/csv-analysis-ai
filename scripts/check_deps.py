try:
    import fastapi
    import uvicorn
    import python_multipart
    print("✅ FastAPI, Uvicorn, and Python-Multipart are installed.")
    print(f"FastAPI version: {fastapi.__version__}")
    print(f"Uvicorn version: {uvicorn.__version__}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
