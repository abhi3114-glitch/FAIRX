from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import base64, json, cv2, asyncio, os, time

from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
from .config import CFG
from .startup import start_all_threads, restart_vision_thread

app = FastAPI(title="FAIRX")

# Serve evidence directory
os.makedirs(CFG.evidence_dir, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=CFG.evidence_dir), name="evidence")


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


# Enhanced HTML with camera selection and video upload
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>FAIRX Monitor</title>
<style>
body { font-family: Arial; padding: 20px; background: #f0f0f0; }
h2 { color: #333; }
.container { display: flex; gap: 30px; }
.video-box, .score-box {
  background: #fff; padding: 20px; border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
}
#cam { border: 2px solid #222; border-radius: 6px; width: 640px; }
#score { font-size: 48px; font-weight: bold; }
#score.warning { color: #f39c12; }
#score.danger { color: #e74c3c; }
#score.ok { color: #2ecc71; }
.status { padding: 10px; margin: 10px 0; border-radius: 4px; }
.status.connected { background: #d4edda; color: #155724; }
.status.disconnected { background: #f8d7da; color: #721c24; }
#log { height: 260px; overflow: auto; background: #fafafa; padding: 8px; border-radius: 4px; }
#log li { margin: 4px 0; padding: 4px; background: white; border-radius: 3px; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, 180px); gap: 10px; margin-top: 15px; }
.thumb { width: 180px; border-radius: 6px; border: 1px solid #ddd; }
small { font-size: 11px; color: #888; }

/* NEW: Camera controls */
.controls {
  background: #fff; padding: 15px; border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  margin-bottom: 20px;
}
.controls h3 { margin-top: 0; color: #333; }
.control-group {
  display: flex; gap: 15px; align-items: center;
  margin: 10px 0;
}
.control-group label { font-weight: bold; min-width: 120px; }
select, button, input[type="file"] {
  padding: 8px 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 14px;
  cursor: pointer;
}
button {
  background: #3498db;
  color: white;
  border: none;
  font-weight: bold;
  transition: background 0.3s;
}
button:hover { background: #2980b9; }
button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
.info-box {
  background: #e8f4f8;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-size: 13px;
  color: #2c3e50;
}
.success { background: #d4edda; color: #155724; }
.error { background: #f8d7da; color: #721c24; }
</style>
</head>
<body>

<h2>FAIRX Live Monitor ✅</h2>

<!-- NEW: Camera Controls -->
<div class="controls">
  <h3>📹 Camera & Input Settings</h3>
  
  <div class="control-group">
    <label>Camera Source:</label>
    <select id="camSelect">
      <option value="0">Camera 0 (Default)</option>
      <option value="1" selected>Camera 1 (Camo Studio)</option>
      <option value="2">Camera 2</option>
      <option value="3">Camera 3</option>
      <option value="4">Camera 4</option>
    </select>
    <button onclick="changeCamera()">Switch Camera</button>
    <button onclick="detectCameras()">Detect Available</button>
  </div>
  
  <div class="control-group">
    <label>Test with Video File:</label>
    <input type="file" id="videoFile" accept="video/*">
    <button onclick="uploadVideo()" id="uploadBtn">Use Video File</button>
  </div>
  
  <div id="infoBox" class="info-box" style="display:none;"></div>
</div>

<div id="status-video" class="status disconnected">📹 Video: Connecting...</div>
<div id="status-score" class="status disconnected">📊 Score: Connecting...</div>

<div class="container">
  <div class="video-box">
    <h3>Camera Feed <small id="fps"></small></h3>
    <img id="cam">
    <div id="lat" style="font-size:12px; color:#666; margin-top:6px"></div>
  </div>

  <div class="score-box">
    <h3>Suspicion Score</h3>
    <div id='score' class="ok">0.00</div>

    <h4>Events</h4>
    <ul id='log'></ul>

    <button onclick="loadEv()">📦 Refresh Evidence</button>
    <a href="/evidence/log.jsonl" target="_blank">View Raw Logs</a>
  </div>
</div>

<h3>Evidence</h3>
<div id="ev" class="grid"></div>

<script>
const WS = path => (location.protocol === "https:" ? "wss://" : "ws://") + location.host + path;

function setStatus(id, connected) {
  const el = document.getElementById(id);
  el.className = "status " + (connected ? "connected" : "disconnected");
  el.textContent = (id === "status-video" ? "📹 Video: " : "📊 Score: ") + (connected ? "Connected" : "Disconnected");
}

function showInfo(message, isError = false) {
  const box = document.getElementById("infoBox");
  box.textContent = message;
  box.className = "info-box " + (isError ? "error" : "success");
  box.style.display = "block";
  setTimeout(() => box.style.display = "none", 5000);
}

async function detectCameras() {
  try {
    const res = await fetch("/api/available_cameras");
    const data = await res.json();
    const select = document.getElementById("camSelect");
    select.innerHTML = "";
    
    if (data.cameras.length === 0) {
      showInfo("⚠️ No cameras detected!", true);
      return;
    }
    
    data.cameras.forEach(idx => {
      const opt = document.createElement("option");
      opt.value = idx;
      opt.textContent = `Camera ${idx}${idx === 1 ? " (Camo Studio)" : ""}`;
      select.appendChild(opt);
    });
    
    showInfo(`✅ Found ${data.cameras.length} camera(s): ${data.cameras.join(", ")}`);
  } catch (e) {
    showInfo("❌ Failed to detect cameras: " + e.message, true);
  }
}

async function changeCamera() {
  const camIndex = document.getElementById("camSelect").value;
  try {
    const res = await fetch("/api/set_camera", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({cam_index: parseInt(camIndex)})
    });
    
    const data = await res.json();
    if (data.status === "success") {
      showInfo(`✅ Switched to Camera ${camIndex}`);
      // Reconnect websockets
      setTimeout(() => {
        wsVideo.close();
        wsVideo = new WebSocket(WS("/video"));
        setupVideoWS();
      }, 1000);
    } else {
      showInfo("❌ Failed to switch camera: " + data.message, true);
    }
  } catch (e) {
    showInfo("❌ Error switching camera: " + e.message, true);
  }
}

async function uploadVideo() {
  const fileInput = document.getElementById("videoFile");
  const file = fileInput.files[0];
  
  if (!file) {
    showInfo("⚠️ Please select a video file first!", true);
    return;
  }
  
  showInfo("📹 Video file mode is for local testing. Please run the system locally with your video file path in the code.");
  showInfo("💡 Tip: For demo recording, use OBS or screen recording software to capture the live feed.", false);
}

async function loadEv() {
  const res = await fetch("/api/evidence?limit=30");
  const data = await res.json();
  const el = document.getElementById("ev");
  el.innerHTML = "";
  for (let x of data) {
    el.innerHTML += `
      <div>
        <a href="/evidence/${x.image}" target="_blank">
          <img src="/evidence/${x.image}" class="thumb">
        </a>
        <div><small>${x.ts}<br>${x.kind} (${x.confidence})</small></div>
      </div>`;
  }
}
loadEv();

let wsScore = new WebSocket(WS("/ws"));
let wsVideo = new WebSocket(WS("/video"));

wsScore.onopen = () => setStatus("status-score", true);
wsScore.onclose = () => setStatus("status-score", false);

wsScore.onmessage = e => {
  let d = JSON.parse(e.data);
  let score = d.score;
  let el = document.getElementById("score");
  el.textContent = score.toFixed(2);
  el.className = score > 0.7 ? "danger" : score > 0.4 ? "warning" : "ok";

  if (d.last_event) {
    let li = document.createElement("li");
    li.textContent = `${d.last_event.kind} (${d.last_event.confidence.toFixed(2)})`;
    document.getElementById("log").prepend(li);
  }
};

function setupVideoWS() {
  wsVideo.onopen = () => setStatus("status-video", true);
  wsVideo.onclose = () => setStatus("status-video", false);
  
  let frames = 0, last = performance.now();
  wsVideo.onmessage = e => {
    const t = performance.now();
    frames++;
    if (frames % 20 === 0) {
      const fps = (frames * 1000 / (t - last)).toFixed(1);
      document.getElementById("fps").textContent = `(${fps} FPS)`;
    }
    document.getElementById("lat").textContent = `Latency: ${(performance.now() - t).toFixed(1)} ms`;
    document.getElementById("cam").src = "data:image/jpeg;base64," + e.data;
  };
}

setupVideoWS();

// Set default camera to 1 (Camo Studio)
document.getElementById("camSelect").value = "1";
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
    print("[SERVER] ✅ Score WS connected")
    try:
        while True:
            await ws.send_text(json.dumps({
                "score": SCORE.score(),
                "last_event": SCORE.last_event.dict() if SCORE.last_event else None
            }))
            await asyncio.sleep(0.2)
    except Exception:
        print("[SERVER] ❌ Score WS closed")


@app.websocket("/video")
async def ws_video(ws: WebSocket):
    await ws.accept()
    print("[SERVER] ✅ Video WS connected")
    try:
        while True:
            with FRAME_BUFFER.lock:
                frame = FRAME_BUFFER.frame.copy() if FRAME_BUFFER.frame is not None else None

            if frame is None:
                await asyncio.sleep(0.03)
                continue

            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if ok:
                await ws.send_text(base64.b64encode(buf).decode())
            await asyncio.sleep(0.03)

    except Exception:
        print("[SERVER] ❌ Video WS closed")


@app.on_event("startup")
async def start_threads():
    start_all_threads()
    print("✅ All FAIRX threads started")