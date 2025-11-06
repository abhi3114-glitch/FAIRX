from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
import base64, json, cv2, asyncio

app = FastAPI(title="FAIRX")

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>FAIRX Monitor</title>
  <style>
    body { font-family: Arial; padding: 20px; background: #f0f0f0; }
    h2 { color: #333; }
    .container { display: flex; gap: 30px; }
    .video-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .score-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    #cam { border: 2px solid #333; border-radius: 4px; max-width: 100%; }
    #score { font-size: 48px; font-weight: bold; color: #2ecc71; margin: 10px 0; }
    #score.warning { color: #f39c12; }
    #score.danger { color: #e74c3c; }
    #log { height: 300px; overflow: auto; background: #f9f9f9; padding: 10px; border-radius: 4px; }
    #log li { margin: 5px 0; padding: 5px; background: white; border-radius: 3px; }
    .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
    .status.connected { background: #d4edda; color: #155724; }
    .status.disconnected { background: #f8d7da; color: #721c24; }
  </style>
</head>
<body>

<h2>FAIRX Live Monitor ✅</h2>

<div id="status-video" class="status disconnected">📹 Video: Connecting...</div>
<div id="status-score" class="status disconnected">📊 Score: Connecting...</div>

<div class="container">
  <div class="video-box">
    <h3>Camera Feed</h3>
    <img id='cam' width="640">
  </div>

  <div class="score-box">
    <h3>Suspicion Score</h3>
    <div id='score'>0.00</div>
    <h4>Recent Events</h4>
    <ul id='log'></ul>
  </div>
</div>

<script>
function WS(path) {
  const proto = location.protocol === "https:" ? "wss://" : "ws://";
  return proto + location.host + path;
}

console.log("[BROWSER] Connecting WebSockets...");

let wsScore = new WebSocket(WS("/ws"));
let wsVideo = new WebSocket(WS("/video"));

// Score WebSocket
wsScore.onopen = () => {
  console.log("[BROWSER] ✅ Score WS connected");
  document.getElementById("status-score").className = "status connected";
  document.getElementById("status-score").textContent = "📊 Score: Connected";
};

wsScore.onclose = () => {
  console.log("[BROWSER] ❌ Score WS closed");
  document.getElementById("status-score").className = "status disconnected";
  document.getElementById("status-score").textContent = "📊 Score: Disconnected";
};

wsScore.onerror = e => {
  console.log("[BROWSER] ⚠ Score WS error", e);
};

wsScore.onmessage = e => {
  let d = JSON.parse(e.data);
  let scoreEl = document.getElementById("score");
  let score = d.score;
  
  scoreEl.innerText = score.toFixed(2);
  
  // Color coding
  scoreEl.className = "";
  if (score > 0.7) scoreEl.className = "danger";
  else if (score > 0.4) scoreEl.className = "warning";

  if(d.last_event){
    let li = document.createElement("li");
    li.textContent = d.last_event.kind + " (" + d.last_event.confidence.toFixed(2) + ")";
    document.getElementById("log").prepend(li);
    
    // Keep only last 50 events
    let log = document.getElementById("log");
    while(log.children.length > 50) {
      log.removeChild(log.lastChild);
    }
  }
};

// Video WebSocket
wsVideo.onopen = () => {
  console.log("[BROWSER] ✅ Video WS connected");
  document.getElementById("status-video").className = "status connected";
  document.getElementById("status-video").textContent = "📹 Video: Connected";
};

wsVideo.onclose = () => {
  console.log("[BROWSER] ❌ Video WS closed");
  document.getElementById("status-video").className = "status disconnected";
  document.getElementById("status-video").textContent = "📹 Video: Disconnected";
};

wsVideo.onerror = e => {
  console.log("[BROWSER] ⚠ Video WS error", e);
};

let frameCount = 0;
wsVideo.onmessage = e => {
  frameCount++;
  if(frameCount % 30 == 0) {
    console.log("[BROWSER] Received", frameCount, "frames, latest size:", e.data.length);
  }
  
  if(e.data.length > 20) {
    document.getElementById("cam").src = "data:image/jpeg;base64," + e.data;
  }
};
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
    except Exception as e:
        print(f"[SERVER] ❌ Score WS disconnected: {e}")

@app.websocket("/video")
async def ws_video(ws: WebSocket):
    await ws.accept()
    print("[SERVER] ✅ Video WS connected")
    frame_count = 0
    try:
        while True:
            with FRAME_BUFFER.lock:
                frame = None if FRAME_BUFFER.frame is None else FRAME_BUFFER.frame.copy()

            if frame is None:
                await asyncio.sleep(0.05)
                continue

            ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ok:
                continue

            b64 = base64.b64encode(buffer).decode()
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"[SERVER] Sent {frame_count} frames, latest size: {len(b64)} bytes")

            await ws.send_text(b64)
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print(f"[SERVER] ❌ Video WS disconnected: {e}")

# Auto-start threads when FastAPI starts
@app.on_event("startup")
async def startup_event():
    """Initialize all monitoring threads on server startup"""
    from .startup import start_all_threads
    start_all_threads()