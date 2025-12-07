import os
import uuid
import aiofiles
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY")

app = FastAPI(title="Typare Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/api/transcribe")
async def api_transcribe(file: UploadFile = File(...)):
    tmp_path = f"/tmp/{uuid.uuid4().hex}_{file.filename}"
    async with aiofiles.open(tmp_path, "wb") as f:
        await f.write(await file.read())

    if not OPENAI_KEY:
        return {"mock": True, "text": "Mock mode - no API key"}

    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    files = {"file": open(tmp_path, "rb")}
    data = {"model": "whisper-1"}

    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, headers=headers, files=files, data=data)

    r.raise_for_status()
    return r.json()

@app.post("/api/tts")
async def api_tts(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(400, "Missing text")

    # If ElevenLabs is configured
    if ELEVENLABS_KEY:
        el_url = "https://api.elevenlabs.io/v1/text-to-speech/default"
        headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
        body = {"text": text}
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(el_url, headers=headers, json=body)
        r.raise_for_status()
        out_path = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
        with open(out_path, "wb") as f:
            f.write(r.content)
        return FileResponse(out_path, media_type="audio/mpeg")

    # Default: OpenAI TTS
    if not OPENAI_KEY:
        raise HTTPException(500, "TTS unavailable: no API key")

    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    body = {"model": "gpt-tts-1", "input": text}

    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, headers=headers, json=body)

    r.raise_for_status()
    out_path = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
    with open(out_path, "wb") as f:
        f.write(r.content)

    return FileResponse(out_path, media_type="audio/mpeg")

@app.post("/api/voice-commands")
async def api_voice_commands(payload: dict):
    text = payload.get("text", "")

    if not OPENAI_KEY:
        return {"mock": True, "intent": "mock", "text": text}

    url = "https://api.openai.com/v1/responses"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

    body = {
        "model": "gpt-5-mini",
        "input": (
            "Analizza il comando vocale e restituisci JSON nel formato: "
            "{intent: string, entities: object}. "
            f"Testo: {text}"
        )
    }

    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.post(url, headers=headers, json=body)

    r.raise_for_status()
    return r.json()
