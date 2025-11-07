from fastapi import FastAPI, WebSocket, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import base64, json, cv2, asyncio, os, time
from pathlib import Path
import tempfile

from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
from .config import CFG
from .startup import start_all_threads, restart_vision_thread, stop_vision_thread, start_video_file_mode

app = FastAPI(title="FAIRX")

# Serve evidence directory
os.makedirs(CFG.evidence_dir, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=CFG.evidence_dir), name="evidence")

# Store uploaded video path
video_mode_active = False
current_video_path = None


@app.get("/api/evidence")
async def evidence_api(limit: int = 50):
    items = []
    log_file = os.path.join(CFG.evidence_dir, "log.jsonl")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()[-limit:][::-1]
            for ln in lines:
                try: items.append(json.loads(ln))
                except: pass
    return JSONResponse(items)


@app.post("/api/set_camera")
async def set_camera(data: dict):
    """Change camera index dynamically"""
    global video_mode_active, current_video_path
    try:
        cam_index = int(data.get("cam_index", 0))
        CFG.cam_index = cam_index
        
        # Disable video mode if switching to camera
        video_mode_active = False
        current_video_path = None
        
        restart_vision_thread(cam_index)
        return JSONResponse({"status": "success", "cam_index": cam_index})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/api/available_cameras")
async def available_cameras():
    """Detect available camera indices"""
    available = []
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
        await asyncio.sleep(0.05)  # Small delay to prevent resource issues
    return JSONResponse({"cameras": available})


@app.post("/api/upload_video")
async def upload_video(video: UploadFile = File(...)):
    """Upload and use video file instead of camera"""
    global video_mode_active, current_video_path
    
    try:
        # Create temp directory if not exists
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        video_path = temp_dir / f"uploaded_{int(time.time())}_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        # Stop camera thread and start video mode
        stop_vision_thread()
        current_video_path = str(video_path)
        video_mode_active = True
        
        # Start video file processing
        start_video_file_mode(current_video_path)
        
        return JSONResponse({
            "status": "success", 
            "message": f"Video file loaded: {video.filename}",
            "path": str(video_path)
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/api/status")
async def get_status():
    """Get current system status"""
    return JSONResponse({
        "video_mode": video_mode_active,
        "camera_index": CFG.cam_index if not video_mode_active else None,
        "video_path": current_video_path if video_mode_active else None,
        "score": SCORE.score(),
        "model": CFG.yolo_model
    })


# Enhanced HTML with modern UI
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FAIRX - AI Exam Proctoring System</title>
<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
}

header {
  background: white;
  padding: 20px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

h1 {
  font-size: 28px;
  color: #333;
  font-weight: 700;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.card-body {
  padding: 20px;
}

.video-container {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

#cam {
  width: 100%;
  height: auto;
  display: block;
}

.video-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  background: rgba(0,0,0,0.7);
  padding: 10px;
  border-radius: 6px;
  color: white;
  font-size: 12px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-right: 10px;
}

.status-connected {
  background: #10b981;
  color: white;
}

.status-disconnected {
  background: #ef4444;
  color: white;
}

.status-warning {
  background: #f59e0b;
  color: white;
}

.score-display {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 20px;
}

.score-number {
  font-size: 72px;
  font-weight: 700;
  line-height: 1;
  margin: 10px 0;
}

.score-label {
  font-size: 14px;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.score-ok { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.score-warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.score-danger { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }

.controls-section {
  margin-bottom: 20px;
}

.control-group {
  margin-bottom: 15px;
}

.control-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

select, input[type="file"] {
  width: 100%;
  padding: 10px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

select:focus, input[type="file"]:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-block {
  width: 100%;
  margin-top: 10px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-group {
  display: flex;
  gap: 10px;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 14px;
  display: none;
}

.alert-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #10b981;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.alert-info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #3b82f6;
}

.events-log {
  max-height: 300px;
  overflow-y: auto;
  background: #f9fafb;
  border-radius: 6px;
  padding: 10px;
}

.event-item {
  padding: 10px;
  background: white;
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  border-left: 3px solid #667eea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-kind {
  font-weight: 600;
  color: #333;
}

.event-confidence {
  background: #667eea;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.evidence-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s;
}

.evidence-item:hover {
  transform: translateY(-4px);
}

.evidence-img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.evidence-info {
  padding: 10px;
  font-size: 12px;
}

.evidence-time {
  color: #666;
  display: block;
  margin-bottom: 5px;
}

.evidence-kind {
  font-weight: 600;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
}

.stat-box {
  background: #f9fafb;
  padding: 15px;
  border-radius: 6px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.loading {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.file-upload-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
  width: 100%;
}

.file-upload-wrapper input[type=file] {
  position: absolute;
  left: -9999px;
}

.file-upload-label {
  display: block;
  padding: 10px;
  background: #f9fafb;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.file-upload-label:hover {
  border-color: #667eea;
  background: #f3f4f6;
}

.file-name {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.metrics {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  font-size: 12px;
}

.metric {
  flex: 1;
  background: rgba(255,255,255,0.2);
  padding: 8px;
  border-radius: 6px;
}

.metric-label {
  opacity: 0.8;
}

.metric-value {
  font-weight: 600;
  font-size: 16px;
  margin-top: 2px;
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
</style>
</head>
<body>

<div class="container">
  <header>
    <h1>FAIRX - AI Exam Proctoring System</h1>
    <p class="subtitle">Real-time monitoring with advanced detection capabilities</p>
  </header>

  <div id="alertBox" class="alert"></div>

  <div class="main-grid">
    <!-- Left Column: Video Feed -->
    <div>
      <div class="card">
        <div class="card-header">Live Video Feed</div>
        <div class="card-body">
          <div class="video-container">
            <img id="cam" alt="Camera Feed">
            <div class="video-overlay">
              <span id="statusVideo" class="status-badge status-disconnected">Connecting...</span>
              <span id="statusScore" class="status-badge status-disconnected">Score: --</span>
              <span id="fps" class="status-badge status-badge">-- FPS</span>
            </div>
          </div>
          <div id="latency" style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">
            Latency: -- ms
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="card" style="margin-top: 20px;">
        <div class="card-header">Input Controls</div>
        <div class="card-body">
          <div class="controls-section">
            <div class="control-group">
              <label class="control-label">Camera Source</label>
              <select id="camSelect">
                <option value="0">Camera 0 (Default)</option>
                <option value="1">Camera 1</option>
                <option value="2">Camera 2</option>
                <option value="3">Camera 3</option>
              </select>
              <div class="btn-group" style="margin-top: 10px;">
                <button class="btn btn-primary" onclick="changeCamera()">Switch Camera</button>
                <button class="btn btn-secondary" onclick="detectCameras()">
                  <span id="detectCamText">Detect Available</span>
                  <span id="detectCamLoading" class="loading" style="display:none;"></span>
                </button>
              </div>
            </div>

            <div class="control-group">
              <label class="control-label">Or Upload Video File</label>
              <div class="file-upload-wrapper">
                <input type="file" id="videoFile" accept="video/*" onchange="updateFileName()">
                <label for="videoFile" class="file-upload-label">
                  <div>Click to select video file</div>
                  <div class="file-name" id="fileName">No file selected</div>
                </label>
              </div>
              <button class="btn btn-success btn-block" onclick="uploadVideo()" id="uploadBtn">
                <span id="uploadText">Process Video File</span>
                <span id="uploadLoading" class="loading" style="display:none;"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column: Score & Events -->
    <div>
      <div class="score-display score-ok" id="scoreDisplay">
        <div class="score-label">Suspicion Score</div>
        <div class="score-number" id="scoreValue">0.00</div>
        <div class="metrics">
          <div class="metric">
            <div class="metric-label">Alert Level</div>
            <div class="metric-value" id="alertLevel">Normal</div>
          </div>
          <div class="metric">
            <div class="metric-label">Events</div>
            <div class="metric-value" id="eventCount">0</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Recent Events</div>
        <div class="card-body">
          <div class="events-log" id="eventsLog">
            <div style="text-align: center; color: #666; padding: 20px;">
              No events detected yet
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 20px;">
        <div class="card-header">System Stats</div>
        <div class="card-body">
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-value" id="statModel">--</div>
              <div class="stat-label">YOLO Model</div>
            </div>
            <div class="stat-box">
              <div class="stat-value" id="statMode">Camera</div>
              <div class="stat-label">Input Mode</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Evidence Section -->
  <div class="card">
    <div class="card-header">
      Evidence Log
      <button class="btn btn-secondary" onclick="loadEvidence()" style="float: right; padding: 6px 12px; font-size: 12px;">
        Refresh Evidence
      </button>
    </div>
    <div class="card-body">
      <div class="evidence-grid" id="evidenceGrid">
        <div style="text-align: center; color: #666; padding: 40px; grid-column: 1/-1;">
          No evidence captured yet
        </div>
      </div>
    </div>
  </div>
</div>

<script>
const WS_URL = path => (location.protocol === "https:" ? "wss://" : "ws://") + location.host + path;

let wsScore, wsVideo;
let eventCount = 0;
let frameCount = 0;
let lastFrameTime = performance.now();

function showAlert(message, type = 'info') {
  const alertBox = document.getElementById('alertBox');
  alertBox.className = `alert alert-${type}`;
  alertBox.textContent = message;
  alertBox.style.display = 'block';
  setTimeout(() => alertBox.style.display = 'none', 5000);
}

function updateFileName() {
  const input = document.getElementById('videoFile');
  const fileNameDiv = document.getElementById('fileName');
  if (input.files.length > 0) {
    fileNameDiv.textContent = input.files[0].name;
  } else {
    fileNameDiv.textContent = 'No file selected';
  }
}

async function detectCameras() {
  const btn = document.getElementById('detectCamText');
  const loading = document.getElementById('detectCamLoading');
  
  btn.style.display = 'none';
  loading.style.display = 'inline-block';
  
  try {
    const res = await fetch('/api/available_cameras');
    const data = await res.json();
    const select = document.getElementById('camSelect');
    select.innerHTML = '';
    
    if (data.cameras.length === 0) {
      showAlert('No cameras detected', 'error');
      return;
    }
    
    data.cameras.forEach(idx => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `Camera ${idx}${idx === 1 ? ' (External)' : ''}`;
      select.appendChild(opt);
    });
    
    showAlert(`Found ${data.cameras.length} camera(s)`, 'success');
  } catch (e) {
    showAlert('Failed to detect cameras: ' + e.message, 'error');
  } finally {
    btn.style.display = 'inline';
    loading.style.display = 'none';
  }
}

async function changeCamera() {
  const camIndex = document.getElementById('camSelect').value;
  try {
    const res = await fetch('/api/set_camera', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cam_index: parseInt(camIndex)})
    });
    
    const data = await res.json();
    if (data.status === 'success') {
      showAlert(`Switched to Camera ${camIndex}`, 'success');
      document.getElementById('statMode').textContent = 'Camera';
      reconnectWebSockets();
    } else {
      showAlert('Failed to switch camera: ' + data.message, 'error');
    }
  } catch (e) {
    showAlert('Error switching camera: ' + e.message, 'error');
  }
}

async function uploadVideo() {
  const fileInput = document.getElementById('videoFile');
  const file = fileInput.files[0];
  
  if (!file) {
    showAlert('Please select a video file first', 'error');
    return;
  }
  
  const uploadText = document.getElementById('uploadText');
  const uploadLoading = document.getElementById('uploadLoading');
  const uploadBtn = document.getElementById('uploadBtn');
  
  uploadText.style.display = 'none';
  uploadLoading.style.display = 'inline-block';
  uploadBtn.disabled = true;
  
  try {
    const formData = new FormData();
    formData.append('video', file);
    
    const res = await fetch('/api/upload_video', {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    if (data.status === 'success') {
      showAlert('Video file loaded successfully! Processing...', 'success');
      document.getElementById('statMode').textContent = 'Video';
      reconnectWebSockets();
    } else {
      showAlert('Failed to upload video: ' + data.message, 'error');
    }
  } catch (e) {
    showAlert('Error uploading video: ' + e.message, 'error');
  } finally {
    uploadText.style.display = 'inline';
    uploadLoading.style.display = 'none';
    uploadBtn.disabled = false;
  }
}

function reconnectWebSockets() {
  if (wsScore) wsScore.close();
  if (wsVideo) wsVideo.close();
  
  setTimeout(() => {
    connectWebSockets();
  }, 1000);
}

function updateScoreDisplay(score) {
  const scoreValue = document.getElementById('scoreValue');
  const scoreDisplay = document.getElementById('scoreDisplay');
  const alertLevel = document.getElementById('alertLevel');
  
  scoreValue.textContent = score.toFixed(2);
  
  // Update status badge
  document.getElementById('statusScore').textContent = `Score: ${score.toFixed(2)}`;
  document.getElementById('statusScore').className = 'status-badge ' + 
    (score >= 0.65 ? 'status-badge' : score >= 0.40 ? 'status-warning' : 'status-connected');
  
  // Update display class and alert level
  scoreDisplay.className = 'score-display ' + 
    (score >= 0.65 ? 'score-danger' : score >= 0.40 ? 'score-warning' : 'score-ok');
  
  alertLevel.textContent = score >= 0.65 ? 'Danger' : score >= 0.40 ? 'Warning' : 'Normal';
}

function addEventToLog(event) {
  const log = document.getElementById('eventsLog');
  
  // Remove "no events" message if present
  if (log.children.length === 1 && log.children[0].textContent.includes('No events')) {
    log.innerHTML = '';
  }
  
  const eventItem = document.createElement('div');
  eventItem.className = 'event-item';
  eventItem.innerHTML = `
    <div>
      <span class="event-kind">${event.kind}</span>
      <div style="font-size: 11px; color: #666; margin-top: 2px;">
        ${new Date(event.ts * 1000).toLocaleTimeString()}
      </div>
    </div>
    <span class="event-confidence">${event.confidence.toFixed(2)}</span>
  `;
  
  log.insertBefore(eventItem, log.firstChild);
  
  // Keep only last 20 events
  while (log.children.length > 20) {
    log.removeChild(log.lastChild);
  }
  
  eventCount++;
  document.getElementById('eventCount').textContent = eventCount;
}

async function loadEvidence() {
  try {
    const res = await fetch('/api/evidence?limit=30');
    const data = await res.json();
    const grid = document.getElementById('evidenceGrid');
    
    if (data.length === 0) {
      grid.innerHTML = '<div style="text-align: center; color: #666; padding: 40px; grid-column: 1/-1;">No evidence captured yet</div>';
      return;
    }
    
    grid.innerHTML = '';
    for (let item of data) {
      if (item.type === 'image') {
        const evidenceItem = document.createElement('div');
        evidenceItem.className = 'evidence-item';
        evidenceItem.innerHTML = `
          <a href="/evidence/${item.image}" target="_blank">
            <img src="/evidence/${item.image}" class="evidence-img" alt="${item.kind}">
          </a>
          <div class="evidence-info">
            <span class="evidence-time">${item.ts}</span>
            <span class="evidence-kind">${item.kind} (${item.confidence.toFixed(2)})</span>
          </div>
        `;
        grid.appendChild(evidenceItem);
      }
    }
  } catch (e) {
    showAlert('Failed to load evidence: ' + e.message, 'error');
  }
}

async function loadSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    document.getElementById('statModel').textContent = data.model.replace('.pt', '').toUpperCase();
    document.getElementById('statMode').textContent = data.video_mode ? 'Video' : 'Camera';
  } catch (e) {
    console.error('Failed to load system status:', e);
  }
}

function connectWebSockets() {
  // Score WebSocket
  wsScore = new WebSocket(WS_URL('/ws'));
  
  wsScore.onopen = () => {
    document.getElementById('statusScore').className = 'status-badge status-connected';
    document.getElementById('statusScore').textContent = 'Score: Connected';
  };
  
  wsScore.onclose = () => {
    document.getElementById('statusScore').className = 'status-badge status-disconnected';
    document.getElementById('statusScore').textContent = 'Score: Disconnected';
    setTimeout(() => connectWebSockets(), 2000);
  };
  
  wsScore.onmessage = e => {
    const data = JSON.parse(e.data);
    updateScoreDisplay(data.score);
    if (data.last_event) {
      addEventToLog(data.last_event);
    }
  };
  
  // Video WebSocket
  setupVideoWebSocket();
}

function setupVideoWebSocket() {
  wsVideo = new WebSocket(WS_URL('/video'));
  
  wsVideo.onopen = () => {
    document.getElementById('statusVideo').className = 'status-badge status-connected';
    document.getElementById('statusVideo').textContent = 'Video: Connected';
  };
  
  wsVideo.onclose = () => {
    document.getElementById('statusVideo').className = 'status-badge status-disconnected';
    document.getElementById('statusVideo').textContent = 'Video: Disconnected';
    setTimeout(() => setupVideoWebSocket(), 2000);
  };
  
  wsVideo.onmessage = e => {
    const startTime = performance.now();
    document.getElementById('cam').src = 'data:image/jpeg;base64,' + e.data;
    
    frameCount++;
    const now = performance.now();
    
    if (frameCount % 30 === 0) {
      const elapsed = now - lastFrameTime;
      const fps = (30 * 1000 / elapsed).toFixed(1);
      document.getElementById('fps').textContent = `${fps} FPS`;
      lastFrameTime = now;
    }
    
    document.getElementById('latency').textContent = `Latency: ${(performance.now() - startTime).toFixed(1)} ms`;
  };
}

// Initialize
connectWebSockets();
loadEvidence();
loadSystemStatus();

// Auto-refresh evidence every 30 seconds
setInterval(loadEvidence, 30000);
</script>

</body>
</html>
"""

@app.get("/")
async def index():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def ws_score(ws: WebSocket):
    await ws.accept()
    print("[SERVER] Score WS connected")
    try:
        while True:
            await ws.send_text(json.dumps({
                "score": SCORE.score(),
                "last_event": SCORE.last_event.dict() if SCORE.last_event else None
            }))
            await asyncio.sleep(0.2)
    except Exception:
        print("[SERVER] Score WS closed")


@app.websocket("/video")
async def ws_video(ws: WebSocket):
    await ws.accept()
    print("[SERVER] Video WS connected")
    try:
        while True:
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None

            if frame is None:
                await asyncio.sleep(0.03)
                continue

            # Compress more aggressively for better performance
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            if ok:
                await ws.send_text(base64.b64encode(buf).decode())
            await asyncio.sleep(0.033)  # ~30 FPS

    except Exception:
        print("[SERVER] Video WS closed")


@app.on_event("startup")
async def start_threads():
    start_all_threads()
    print("All FAIRX threads started")