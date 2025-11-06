from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from .suspicion import SCORE
from .frame_buffer import FRAME_BUFFER
import base64, json, cv2, asyncio

app = FastAPI(title="FAIRX")

HTML = """
<h2>FAIRX Live Monitor ✅</h2>

<div style="display:flex; gap:30px">

  <div>
    <h3>Camera Feed</h3>
    <img id='cam' width="450" style="border:2px solid black">
  </div>

  <div>
    <h3>Suspicion Score</h3>
    <div style='font-size:48px' id='score'>0.00</div>
    <ul id='log' style="height:300px; overflow:auto;"></ul>
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

wsScore.onopen = () => console.log("[BROWSER] ✅ Score WS connected");
wsScore.onclose = () => console.log("[BROWSER] ❌ Score WS closed");
wsScore.onerror = e => console.log("[BROWSER] ⚠ Score WS error", e);

wsScore.onmessage = e => {
  let d = JSON.parse(e.data);
  document.getElementById("score").innerText = d.score.toFixed(2);

  if(d.last_event){
    let li = document.createElement("li");
    li.textContent = d.last_event.kind + " (" + d.last_event.confidence.toFixed(2) + ")";
    document.getElementById("log").prepend(li);
  }
};

wsVideo.onopen = () => console.log("[BROWSER] ✅ Video WS connected");
wsVideo.onclose = () => console.log("[BROWSER] ❌ Video WS closed");
wsVideo.onerror = e => console.log("[BROWSER] ⚠ Video WS error", e);

wsVideo.onmessage = e => {
  console.log("[BROWSER] frame len:", e.data.length);
  if(e.data.length > 20) {
    document.getElementById("cam").src = "data:image/jpeg;base64," + e.data;
  }
};
</script>
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
    except:
        print("[SERVER] ❌ Score WS disconnected")

@app.websocket("/video")
async def ws_video(ws: WebSocket):
    await ws.accept()
    print("[SERVER] ✅ Video WS connected")
    try:
        while True:
            with FRAME_BUFFER.lock:
                frame = None if FRAME_BUFFER.frame is None else FRAME_BUFFER.frame.copy()

            if frame is None:
                await asyncio.sleep(0.01)
                continue

            ok, buffer = cv2.imencode(".jpg", frame)
            if not ok:
                continue

            b64 = base64.b64encode(buffer).decode()
            print("[SERVER] sending frame size:", len(b64))

            await ws.send_text(b64)
            await asyncio.sleep(0.03)
    except:
        print("[SERVER] ❌ Video WS disconnected")
