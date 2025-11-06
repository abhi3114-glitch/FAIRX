@echo off
echo ========================================
echo   FAIRX - Starting System
echo ========================================

REM Activate virtual environment
if not exist .venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

call .venv\Scripts\activate

echo.
echo Checking if YOLO model exists...
if not exist yolov8n.pt (
    echo Downloading YOLOv8 model on first run...
)

echo.
echo Starting FAIRX server on http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

uvicorn src.fairx.server:app --host 0.0.0.0 --port 8000 --reload

pause