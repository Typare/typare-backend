import os
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# =========================
# OpenAI client (SDK)
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# Modello dati per la dettatura
# =========================
class Dictation(BaseModel):
    text: str

# Buffer in memoria (fondamenta)
BUFFER = []

# =========================
# Endpoints base
# =========================
@app.get("/")
def root():
    return {"status": "Typare live – foundations OK"}

@app.get("/health")
def health():
    return {"ok": True}

# =========================
# Dictation base
# =========================
@app.post("/dictate")
def dictate(data: Dictation):
    BUFFER.append(data.text)
    return {
        "message": "Text received",
        "buffer": BUFFER
    }

@app.get("/buffer")
def read_buffer():
    return {"buffer": BUFFER}

# =========================
# Mock transcription
# =========================
@app.get("/mock/transcribe")
async def mock_transcribe_get():
    return {"text": "TEST DI TRASCRIZIONE OK"}

# =========================
# UI statica
# =========================
app.mount("/ui", StaticFiles(directory="static", html=True), name="static")

# =========================
# Wire test (reale, senza audio)
# =========================
@app.post("/transcribe")
async def transcribe():
    return {"text": "TRASCRIZIONE REALE COLLEGATA"}

# =========================
# Whisper reale via SDK OpenAI
# =========================
@app.post("/transcribe/audio")
async def transcribe_audio(file: UploadFile = File(...)):
    if not os.getenv("OPENAI_API_KEY"):
        return {"text": "ERRORE: OPENAI_API_KEY mancante"}

    # salva audio temporaneo
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # chiamata Whisper tramite SDK ufficiale
    with open(tmp_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    os.unlink(tmp_path)
    return {"text": transcript.text}
