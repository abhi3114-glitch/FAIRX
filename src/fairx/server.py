"""
FAIRX Web Server - Fixed and Enhanced
FastAPI server with camera selection and monitoring
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import base64
import json
import asyncio
import logging
from typing import List
import numpy as np

from .config import Config
from .vision import VisionDetector
from .suspicion import SuspicionTracker
from .events import EventLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FAIRX Proctoring System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vision_detector = VisionDetector()
suspicion_tracker = SuspicionTracker()
event_logger = EventLogger()

# Active camera
current_camera = None
camera_index = Config.cam_index

def get_camera(index: int = 0):
    """Initialize camera with error handling"""
    try:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            raise Exception(f"Cannot open camera {index}")
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.camera_resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.camera_resolution[1])
        cap.set(cv2.CAP_PROP_FPS, Config.fps)
        
        logger.info(f"Camera {index} initialized successfully")
        return cap
    except Exception as e:
        logger.error(f"Camera initialization error: {e}")
        return None

def release_camera():
    """Safely release camera"""
    global current_camera
    if current_camera is not None:
        current_camera.release()
        current_camera = None

@app.get("/")
async def get_home():
    """Main dashboard HTML"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAIRX - AI Exam Proctoring</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 30px; }
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        button:hover { background: #5568d3; transform: translateY(-2px); }
        button:active { transform: translateY(0); }
        select {
            padding: 12px;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-size: 1em;
            min-width: 200px;
        }
        .video-container {
            position: relative;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        #videoFeed {
            width: 100%;
            height: auto;
            display: block;
        }
        .alert-bar {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s;
        }
        .alert-normal { background: #10b981; color: white; }
        .alert-warning { background: #f59e0b; color: white; }
        .alert-danger { background: #ef4444; color: white; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: #f3f4f6;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card h3 { color: #667eea; margin-bottom: 10px; }
        .stat-card p { font-size: 2em; font-weight: bold; color: #333; }
        .log-container {
            background: #f9fafb;
            border-radius: 12px;
            padding: 20px;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .log-entry {
            padding: 10px;
            margin-bottom: 8px;
            background: white;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background: #10b981; }
        .status-inactive { background: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 FAIRX</h1>
            <p>Advanced AI-Powered Exam Proctoring System</p>
        </div>
        
        <div class="content">
            <div class="controls">
                <button onclick="detectCameras()">🔍 Detect Cameras</button>
                <select id="cameraSelect">
                    <option value="0">Camera 0 (Default)</option>
                </select>
                <button onclick="switchCamera()">📷 Switch Camera</button>
                <button onclick="startMonitoring()">▶️ Start Monitoring</button>
                <button onclick="stopMonitoring()">⏸️ Stop Monitoring</button>
                <div style="margin-left: auto;">
                    <span class="status-indicator status-inactive" id="statusIndicator"></span>
                    <span id="statusText">Inactive</span>
                </div>
            </div>
            
            <div id="alertBar" class="alert-bar alert-normal">
                System Ready - No Suspicious Activity
            </div>
            
            <div class="video-container">
                <img id="videoFeed" src="" alt="Video Feed">
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Suspicion Score</h3>
                    <p id="suspicionScore">0.00</p>
                </div>
                <div class="stat-card">
                    <h3>Events Detected</h3>
                    <p id="eventCount">0</p>
                </div>
                <div class="stat-card">
                    <h3>Current Camera</h3>
                    <p id="currentCamera">0</p>
                </div>
                <div class="stat-card">
                    <h3>FPS</h3>
                    <p id="fps">0</p>
                </div>
            </div>
            
            <div class="log-container">
                <h3 style="margin-bottom: 15px; color: #667eea;">📋 Activity Log</h3>
                <div id="logEntries"></div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let isMonitoring = false;
        let eventCount = 0;

        function detectCameras() {
            fetch('/api/detect-cameras')
                .then(res => res.json())
                .then(data => {
                    const select = document.getElementById('cameraSelect');
                    select.innerHTML = '';
                    data.cameras.forEach(cam => {
                        const option = document.createElement('option');
                        option.value = cam.index;
                        option.textContent = `Camera ${cam.index}`;
                        select.appendChild(option);
                    });
                    addLog('✅ Detected ' + data.cameras.length + ' camera(s)');
                })
                .catch(err => addLog('❌ Camera detection failed: ' + err));
        }

        function switchCamera() {
            const index = document.getElementById('cameraSelect').value;
            fetch('/api/switch-camera', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({camera_index: parseInt(index)})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('currentCamera').textContent = index;
                addLog('📷 Switched to camera ' + index);
            })
            .catch(err => addLog('❌ Camera switch failed: ' + err));
        }

        function startMonitoring() {
            if (isMonitoring) return;
            
            ws = new WebSocket('ws://localhost:8000/ws');
            
            ws.onopen = () => {
                isMonitoring = true;
                document.getElementById('statusIndicator').className = 'status-indicator status-active';
                document.getElementById('statusText').textContent = 'Active';
                addLog('🟢 Monitoring started');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                // Update video feed
                document.getElementById('videoFeed').src = 'data:image/jpeg;base64,' + data.frame;
                
                // Update stats
                document.getElementById('suspicionScore').textContent = data.suspicion_score.toFixed(2);
                document.getElementById('fps').textContent = data.fps || 0;
                
                // Update alert bar
                updateAlertBar(data.suspicion_score, data.alert_level);
                
                // Log events
                if (data.events && data.events.length > 0) {
                    data.events.forEach(event => {
                        eventCount++;
                        document.getElementById('eventCount').textContent = eventCount;
                        addLog(`⚠️ ${event.type}: ${event.description}`);
                    });
                }
            };
            
            ws.onerror = (error) => {
                addLog('❌ WebSocket error: ' + error);
            };
            
            ws.onclose = () => {
                isMonitoring = false;
                document.getElementById('statusIndicator').className = 'status-indicator status-inactive';
                document.getElementById('statusText').textContent = 'Inactive';
                addLog('🔴 Monitoring stopped');
            };
        }

        function stopMonitoring() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }

        function updateAlertBar(score, level) {
            const bar = document.getElementById('alertBar');
            
            if (score < 0.40) {
                bar.className = 'alert-bar alert-normal';
                bar.textContent = `✅ Normal Activity - Score: ${score.toFixed(2)}`;
            } else if (score < 0.65) {
                bar.className = 'alert-bar alert-warning';
                bar.textContent = `⚠️ WARNING - Suspicious Activity Detected - Score: ${score.toFixed(2)}`;
            } else {
                bar.className = 'alert-bar alert-danger';
                bar.textContent = `🚨 DANGER - High Cheating Probability - Score: ${score.toFixed(2)}`;
            }
        }

        function addLog(message) {
            const logEntries = document.getElementById('logEntries');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${message}`;
            logEntries.insertBefore(entry, logEntries.firstChild);
            
            // Keep only last 50 entries
            while (logEntries.children.length > 50) {
                logEntries.removeChild(logEntries.lastChild);
            }
        }

        // Auto-detect cameras on page load
        window.onload = () => {
            detectCameras();
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/detect-cameras")
async def detect_cameras():
    """Detect available cameras"""
    cameras = []
    for i in range(5):  # Check first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append({"index": i, "available": True})
            cap.release()
    
    return JSONResponse({"cameras": cameras, "count": len(cameras)})

@app.post("/api/switch-camera")
async def switch_camera(data: dict):
    """Switch to a different camera"""
    global camera_index, current_camera
    
    try:
        new_index = data.get("camera_index", 0)
        release_camera()
        camera_index = new_index
        current_camera = get_camera(camera_index)
        
        if current_camera:
            return JSONResponse({"success": True, "camera_index": camera_index})
        else:
            return JSONResponse({"success": False, "error": "Failed to open camera"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time video streaming"""
    await websocket.accept()
    
    global current_camera
    if current_camera is None:
        current_camera = get_camera(camera_index)
    
    try:
        frame_count = 0
        import time
        start_time = time.time()
        
        while True:
            if current_camera is None or not current_camera.isOpened():
                await websocket.send_json({"error": "Camera not available"})
                break
            
            ret, frame = current_camera.read()
            if not ret:
                await websocket.send_json({"error": "Failed to read frame"})
                continue
            
            # Detect objects
            detections, annotated_frame = vision_detector.detect_objects(frame)
            
            # Update suspicion score
            events = []
            for det in detections:
                suspicion_tracker.add_event(det['type'], det.get('confidence', 0.5))
                events.append({
                    'type': det['type'],
                    'description': f"{det['object']} detected (conf: {det['confidence']:.2f})"
                })
            
            suspicion_score = suspicion_tracker.get_score()
            alert_level = "normal"
            if suspicion_score >= Config.alert_threshold_danger:
                alert_level = "danger"
            elif suspicion_score >= Config.alert_threshold_warning:
                alert_level = "warning"
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Send data
            await websocket.send_json({
                'frame': frame_base64,
                'suspicion_score': suspicion_score,
                'alert_level': alert_level,
                'events': events,
                'fps': int(fps),
                'camera_index': camera_index
            })
            
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        release_camera()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.server_host, port=Config.server_port)