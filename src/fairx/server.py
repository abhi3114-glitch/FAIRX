from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import base64, json, cv2, asyncio, os, time, shutil
from pathlib import Path

from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
from .config import CFG
from .startup import start_all_threads, restart_vision_thread, switch_to_video_file

app = FastAPI(title="FAIRX")

# Serve evidence and upload directories
os.makedirs(CFG.evidence_dir, exist_ok=True)
os.makedirs(CFG.upload_dir, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=CFG.evidence_dir), name="evidence")
app.mount("/uploads", StaticFiles(directory=CFG.upload_dir), name="uploads")


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
    try:
        cam_index = int(data.get("cam_index", 0))
        CFG.cam_index = cam_index
        CFG.video_file_path = None  # Clear video file path
        restart_vision_thread(cam_index)
        return JSONResponse({"status": "success", "cam_index": cam_index})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/api/available_cameras")
async def available_cameras():
    """Detect available camera indices"""
    available = []
    for i in range(5):  # Check first 5 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return JSONResponse({"cameras": available})


@app.post("/api/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file and switch to it as source"""
    try:
        # Save uploaded file
        file_path = Path(CFG.upload_dir) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"[SERVER] Video uploaded: {file_path}")
        
        # Switch to video file
        CFG.video_file_path = str(file_path)
        switch_to_video_file(str(file_path))
        
        return JSONResponse({
            "status": "success",
            "message": f"Video file uploaded and activated: {file.filename}",
            "file_path": str(file_path)
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Failed to upload video: {str(e)}"
        }, status_code=400)


@app.get("/api/system_status")
async def system_status():
    """Get current system status"""
    return JSONResponse({
        "source_type": "video" if CFG.video_file_path else "camera",
        "source": CFG.video_file_path or CFG.cam_index,
        "suspicion_score": SCORE.score(),
        "modules": {
            "audio": CFG.ENABLE_AUDIO,
            "identity": CFG.ENABLE_IDENTITY,
            "screen_agent": CFG.ENABLE_SCREEN_AGENT,
            "hand_detection": CFG.ENABLE_HAND_DETECTION,
            "movement_detection": CFG.ENABLE_MOVEMENT_DETECTION
        }
    })


# Enhanced HTML Dashboard - Clean Professional Design (NO EMOJIS)
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
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

h1 {
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.subtitle {
  color: #666;
  font-size: 14px;
  margin-top: 5px;
}

.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

#cam {
  width: 100%;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  display: block;
}

.video-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 13px;
  color: #666;
}

.score-display {
  text-align: center;
  padding: 30px 0;
}

.score-value {
  font-size: 64px;
  font-weight: bold;
  margin: 20px 0;
}

.score-value.ok { color: #10b981; }
.score-value.warning { color: #f59e0b; }
.score-value.danger { color: #ef4444; }

.score-label {
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status-indicator {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-indicator.connected { background: #10b981; }
.status-indicator.disconnected { background: #ef4444; }

.status-row {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 14px;
}

.controls-section {
  margin-bottom: 20px;
}

.control-group {
  margin-bottom: 15px;
}

.control-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.control-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

select, input[type="file"] {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
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

.btn-success:hover {
  background: #059669;
}

button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.alert {
  padding: 12px 15px;
  border-radius: 6px;
  margin-top: 10px;
  font-size: 13px;
  display: none;
}

.alert.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #10b981;
}

.alert.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.alert.info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #3b82f6;
}

#event-log {
  max-height: 300px;
  overflow-y: auto;
  background: #f9fafb;
  border-radius: 6px;
  padding: 10px;
}

.event-item {
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  margin-bottom: 6px;
  font-size: 13px;
  border-left: 3px solid #667eea;
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.evidence-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.evidence-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.evidence-thumb {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.evidence-info {
  padding: 10px;
  font-size: 12px;
  color: #666;
}

.loading {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
  flex: 1;
}

.file-input-wrapper input[type=file] {
  position: absolute;
  left: -9999px;
}

.file-input-label {
  display: block;
  padding: 10px 15px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  text-align: center;
  color: #6b7280;
}

.file-input-label:hover {
  background: #f9fafb;
}

.file-selected {
  color: #667eea;
  font-weight: 600;
}
</style>
</head>
<body>

<div class="container">
  <header>
    <h1>FAIRX - AI Exam Proctoring System</h1>
    <div class="subtitle">Real-time monitoring and cheating detection</div>
  </header>

  <div class="card controls-section">
    <div class="card-title">Source Configuration</div>
    
    <div class="control-group">
      <label class="control-label">Camera Source</label>
      <div class="control-row">
        <select id="camSelect">
          <option value="0">Camera 0 (Default)</option>
          <option value="1">Camera 1 (External)</option>
          <option value="2">Camera 2</option>
          <option value="3">Camera 3</option>
          <option value="4">Camera 4</option>
        </select>
        <button class="btn-primary" onclick="changeCamera()">Switch Camera</button>
        <button class="btn-secondary" onclick="detectCameras()">Detect Available</button>
      </div>
    </div>

    <div class="control-group">
      <label class="control-label">Video File Upload</label>
      <div class="control-row">
        <div class="file-input-wrapper">
          <input type="file" id="videoFile" accept="video/*" onchange="updateFileName()">
          <label for="videoFile" class="file-input-label" id="fileLabel">Choose video file...</label>
        </div>
        <button class="btn-success" onclick="uploadVideo()" id="uploadBtn">Upload & Use Video</button>
      </div>
    </div>

    <div id="alertBox" class="alert"></div>
  </div>

  <div class="main-grid">
    <div class="card">
      <div class="card-title">Live Feed</div>
      <img id="cam" alt="Video feed">
      <div class="video-info">
        <span id="fps">FPS: --</span>
        <span id="latency">Latency: --</span>
        <span id="source">Source: Camera 0</span>
      </div>
    </div>

    <div class="card">
      <div class="card-title">System Status</div>
      
      <div class="status-row">
        <span class="status-indicator" id="status-video-indicator"></span>
        <span id="status-video-text">Video: Connecting...</span>
      </div>
      
      <div class="status-row">
        <span class="status-indicator" id="status-score-indicator"></span>
        <span id="status-score-text">Score: Connecting...</span>
      </div>

      <div class="score-display">
        <div class="score-label">Suspicion Score</div>
        <div id="score" class="score-value ok">0.00</div>
      </div>

      <div class="card-title" style="margin-top: 20px;">Recent Events</div>
      <div id="event-log"></div>

      <button class="btn-primary" onclick="loadEvidence()" style="width: 100%; margin-top: 15px;">
        Refresh Evidence
      </button>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Evidence Gallery</div>
    <div id="evidence-grid" class="evidence-grid"></div>
  </div>
</div>

<script>
const WS = path => (location.protocol === "https:" ? "wss://" : "ws://") + location.host + path;

let wsScore, wsVideo;
let selectedFileName = "";

function setStatus(type, connected) {
  const indicator = document.getElementById(`status-${type}-indicator`);
  const text = document.getElementById(`status-${type}-text`);
  
  indicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
  text.textContent = `${type === 'video' ? 'Video' : 'Score'}: ${connected ? 'Connected' : 'Disconnected'}`;
}

function showAlert(message, type = 'info') {
  const box = document.getElementById('alertBox');
  box.textContent = message;
  box.className = `alert ${type}`;
  box.style.display = 'block';
  setTimeout(() => box.style.display = 'none', 5000);
}

function updateFileName() {
  const input = document.getElementById('videoFile');
  const label = document.getElementById('fileLabel');
  if (input.files.length > 0) {
    selectedFileName = input.files[0].name;
    label.textContent = selectedFileName;
    label.classList.add('file-selected');
  }
}

async function detectCameras() {
  try {
    const res = await fetch('/api/available_cameras');
    const data = await res.json();
    const select = document.getElementById('camSelect');
    select.innerHTML = '';
    
    if (data.cameras.length === 0) {
      showAlert('No cameras detected!', 'error');
      return;
    }
    
    data.cameras.forEach(idx => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `Camera ${idx}${idx === 0 ? ' (Default)' : idx === 1 ? ' (External)' : ''}`;
      select.appendChild(opt);
    });
    
    showAlert(`Found ${data.cameras.length} camera(s): ${data.cameras.join(', ')}`, 'success');
  } catch (e) {
    showAlert('Failed to detect cameras: ' + e.message, 'error');
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
      document.getElementById('source').textContent = `Source: Camera ${camIndex}`;
      
      // Reconnect websockets
      setTimeout(() => {
        reconnectWebSockets();
      }, 1000);
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
    showAlert('Please select a video file first!', 'error');
    return;
  }
  
  const uploadBtn = document.getElementById('uploadBtn');
  uploadBtn.disabled = true;
  uploadBtn.innerHTML = '<span class="loading"></span> Uploading...';
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch('/api/upload_video', {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    
    if (data.status === 'success') {
      showAlert(data.message, 'success');
      document.getElementById('source').textContent = `Source: ${file.name}`;
      
      // Reconnect websockets
      setTimeout(() => {
        reconnectWebSockets();
      }, 1000);
    } else {
      showAlert('Failed to upload video: ' + data.message, 'error');
    }
  } catch (e) {
    showAlert('Error uploading video: ' + e.message, 'error');
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload & Use Video';
  }
}

async function loadEvidence() {
  try {
    const res = await fetch('/api/evidence?limit=30');
    const data = await res.json();
    const grid = document.getElementById('evidence-grid');
    
    if (data.length === 0) {
      grid.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No evidence recorded yet</p>';
      return;
    }
    
    grid.innerHTML = '';
    for (let item of data) {
      const div = document.createElement('div');
      div.className = 'evidence-item';
      div.innerHTML = `
        <a href="/evidence/${item.image}" target="_blank">
          <img src="/evidence/${item.image}" class="evidence-thumb" alt="Evidence">
        </a>
        <div class="evidence-info">
          <div><strong>${item.kind}</strong></div>
          <div>Confidence: ${item.confidence}</div>
          <div>${item.ts}</div>
        </div>
      `;
      grid.appendChild(div);
    }
  } catch (e) {
    showAlert('Failed to load evidence: ' + e.message, 'error');
  }
}

function reconnectWebSockets() {
  if (wsVideo) wsVideo.close();
  if (wsScore) wsScore.close();
  
  setTimeout(() => {
    setupWebSockets();
  }, 500);
}

function setupWebSockets() {
  // Score WebSocket
  wsScore = new WebSocket(WS('/ws'));
  
  wsScore.onopen = () => setStatus('score', true);
  wsScore.onclose = () => setStatus('score', false);
  
  wsScore.onmessage = e => {
    let data = JSON.parse(e.data);
    let score = data.score;
    let el = document.getElementById('score');
    el.textContent = score.toFixed(2);
    el.className = 'score-value ' + (score > 0.7 ? 'danger' : score > 0.4 ? 'warning' : 'ok');
    
    if (data.last_event) {
      const log = document.getElementById('event-log');
      const item = document.createElement('div');
      item.className = 'event-item';
      item.textContent = `${data.last_event.kind} (${data.last_event.confidence.toFixed(2)})`;
      log.insertBefore(item, log.firstChild);
      
      // Keep only last 10 events
      while (log.children.length > 10) {
        log.removeChild(log.lastChild);
      }
    }
  };
  
  // Video WebSocket
  wsVideo = new WebSocket(WS('/video'));
  
  wsVideo.onopen = () => setStatus('video', true);
  wsVideo.onclose = () => setStatus('video', false);
  
  let frames = 0, lastTime = performance.now();
  wsVideo.onmessage = e => {
    const now = performance.now();
    frames++;
    
    if (frames % 20 === 0) {
      const fps = (frames * 1000 / (now - lastTime)).toFixed(1);
      document.getElementById('fps').textContent = `FPS: ${fps}`;
      frames = 0;
      lastTime = now;
    }
    
    const latency = (performance.now() - now).toFixed(1);
    document.getElementById('latency').textContent = `Latency: ${latency}ms`;
    document.getElementById('cam').src = 'data:image/jpeg;base64,' + e.data;
  };
}

// Initialize
setupWebSockets();
loadEvidence();
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

            # Use configured JPEG quality for better performance
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, CFG.jpeg_quality])
            if ok:
                await ws.send_text(base64.b64encode(buf).decode())
            await asyncio.sleep(0.03)

    except Exception:
        print("[SERVER] Video WS closed")


@app.on_event("startup")
async def start_threads():
    start_all_threads()
    print("All FAIRX threads started")