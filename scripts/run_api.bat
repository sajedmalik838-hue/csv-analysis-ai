@echo off
echo Starting Gemini CSV Chat API...
echo Server will run at http://127.0.0.1:8000
echo Swagger UI available at http://127.0.0.1:8000/docs
echo.
python fastapi_app.py
if errorlevel 1 (
    echo.
    echo ❌ Server crashed! See error above.
    echo.
    cmd /k
)
pause
