from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modello dati per la dettatura
class Dictation(BaseModel):
    text: str

# Buffer in memoria (fondamenta)
BUFFER = []

@app.get("/")
def root():
    return {"status": "Typare live – foundations OK"}

@app.get("/health")
def health():
    return {"ok": True}

# Primo comportamento reale di Typare
@app.post("/dictate")
def dictate(data: Dictation):
    BUFFER.append(data.text)
    return {
        "message": "Text received",
        "buffer": BUFFER
    }
@app.get("/buffer")
def read_buffer():
    return {
        "buffer": BUFFER
    }
@app.get("/mock/transcribe")
async def mock_transcribe_get():
    return {"text": "TEST DI TRASCRIZIONE OK"}
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")
from fastapi import UploadFile, File

@app.post("/transcribe")
async def transcribe():
    return {"text": "TRASCRIZIONE REALE COLLEGATA"}

from fastapi import UploadFile, File
import tempfile
import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.post("/transcribe/audio")
async def transcribe_audio(file: UploadFile = File(...)):
    if not OPENAI_API_KEY:
        return {"text": "ERRORE: OPENAI_API_KEY mancante"}

    # salva audio temporaneo
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # chiamata Whisper (form-data corretto)
        url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    with open(tmp_path, "rb") as f:
        files = {
            "file": (os.path.basename(tmp_path), f, "audio/wav"),
        }
        data = {
            "model": "whisper-1",
            "response_format": "json",
            "language": "it"
        }

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                url,
                headers=headers,
                files=files,
                data=data
            )


    os.unlink(tmp_path)

    r.raise_for_status()
    return r.json()

