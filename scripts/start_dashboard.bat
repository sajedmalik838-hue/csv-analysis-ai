@echo off
echo ==========================================
echo 🤖 AI Chatbot Dashboard Starter
echo ==========================================
echo.

echo [1/3] Checking requirements...
python -m pip install -r requirements.txt

echo.
echo [2/3] Starting the Dashboard...
echo Dashboard will be available at: http://localhost:8502
echo.
echo Press Ctrl+C to stop the dashboard.
echo.

python -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error: Failed to start the dashboard.
    echo Please make sure you have Python installed and your API key in the .env file.
    pause
)

pause
