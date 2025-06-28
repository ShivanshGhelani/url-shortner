@echo off
echo Starting Universal URL Shortener...
echo.


REM Start the application
echo.
echo =====================================
echo  Universal URL Shortener Starting
echo =====================================
echo.
echo Dashboard: http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000
