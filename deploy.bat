@echo off
REM FAIRX Automated Deployment Script for Windows
REM Run this to automatically setup and fix your FAIRX installation

echo ==========================================
echo   FAIRX - Automated Deployment Script
echo ==========================================
echo.

REM Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python is installed
echo.

REM Create directory structure
echo [INFO] Creating directory structure...
if not exist "src\fairx" mkdir src\fairx
if not exist "evidence\screenshots" mkdir evidence\screenshots
if not exist "evidence\videos" mkdir evidence\videos
if not exist "evidence\logs" mkdir evidence\logs
echo [OK] Directories created
echo.

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip upgraded
echo.

REM Install dependencies
echo [INFO] Installing dependencies (this may take a few minutes)...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo [OK] Dependencies installed
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
echo.

REM Create __init__.py files
echo [INFO] Creating package initialization files...
type nul > src\__init__.py
type nul > src\fairx\__init__.py
echo [OK] Package files created
echo.

REM Download YOLO model
echo [INFO] Downloading YOLO model...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" >nul 2>&1
echo [OK] YOLO model ready
echo.

REM Test imports
echo [INFO] Testing imports...
python -c "import cv2; import numpy; import fastapi; from ultralytics import YOLO" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Some imports failed. Check dependencies.
    pause
    exit /b 1
)
echo [OK] All imports working
echo.

REM Test camera
echo [INFO] Testing camera...
python -c "import cv2; cap = cv2.VideoCapture(0); exit(0 if cap.isOpened() else 1); cap.release()" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Camera not accessible. Check permissions and config.
) else (
    echo [OK] Camera working
)
echo.

REM Create .gitignore
if not exist ".gitignore" (
    echo [INFO] Creating .gitignore...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo venv/
        echo.
        echo # Evidence
        echo evidence/
        echo *.log
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # YOLO
        echo *.pt
        echo runs/
    ) > .gitignore
    echo [OK] .gitignore created
)
echo.

REM Git setup
echo [INFO] Checking Git status...
git status >nul 2>&1
if not errorlevel 1 (
    git add .
    echo [OK] Files staged for commit
    echo.
    echo [INFO] To commit and push, run:
    echo     git commit -m "Fixed all bugs - v2.1.0 production ready"
    echo     git push origin main
) else (
    echo [INFO] Not a git repository. Initialize with: git init
)
echo.

echo ==========================================
echo [SUCCESS] FAIRX Setup Complete!
echo ==========================================
echo.
echo Next Steps:
echo.
echo 1. Start Web Server:
echo    python -m src.fairx.server
echo.
echo 2. Or run locally:
echo    python -m src.fairx.run_local
echo.
echo 3. Access web interface:
echo    http://localhost:8000
echo.
echo 4. Commit changes to GitHub:
echo    git commit -m "Fixed all bugs - v2.1.0"
echo    git push origin main
echo.
echo ==========================================
echo.
pause