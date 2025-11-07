#!/usr/bin/env python3
"""
FAIRX Unified Startup Script
Runs both local display and web server
"""
import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import cv2
        import ultralytics
        import fastapi
        import uvicorn
        import mediapipe
        print("[Check] All dependencies installed")
        return True
    except ImportError as e:
        print(f"[Error] Missing dependency: {e}")
        print("[Fix] Run: pip install -r requirements.txt")
        return False

def check_camera():
    """Check if camera is available"""
    import cv2
    print("[Check] Testing camera...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("[Check] Camera 0 available")
        cap.release()
        return True
    else:
        print("[Warning] Camera 0 not available, will try other indices")
        return False

def run_server_mode():
    """Run FAIRX in web server mode (recommended)"""
    print("\n" + "="*60)
    print("Starting FAIRX Web Server Mode")
    print("="*60)
    print("Dashboard: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.fairx.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n[FAIRX] Server stopped")

def run_local_mode():
    """Run FAIRX in local display mode"""
    print("\n" + "="*60)
    print("Starting FAIRX Local Mode")
    print("="*60)
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m",
            "src.fairx.run_local"
        ])
    except KeyboardInterrupt:
        print("\n\n[FAIRX] Local mode stopped")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   FAIRX - AI Exam Proctoring System                      ║
║   Enhanced Detection & Monitoring                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check camera
    check_camera()
    
    # Choose mode
    print("\nSelect mode:")
    print("  1. Web Server Mode (Recommended) - Dashboard at http://localhost:8000")
    print("  2. Local Mode - OpenCV window display")
    print("  3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n[FAIRX] Cancelled")
        sys.exit(0)
    
    if choice == "1":
        run_server_mode()
    elif choice == "2":
        run_local_mode()
    elif choice == "3":
        print("[FAIRX] Exiting...")
        sys.exit(0)
    else:
        print("[Error] Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()