@echo off
echo ========================================
echo FAIRX - Starting Web Dashboard
echo ========================================
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python -m uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload
pause