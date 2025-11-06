from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import base64, json, cv2, asyncio, os, time

from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
from .config import CFG
from .startup import start_all_threads

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


# ✅ Removed f from f""" ... """
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
</style>
</head>
<body>

<h2>FAIRX Live Monitor ✅</h2>

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

let frames = 0, last = performance.now();
wsVideo.onopen = () => setStatus("status-video", true);
wsVideo.onclose = () => setStatus("status-video", false);

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
