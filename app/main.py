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

