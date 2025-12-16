from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Typare minimal OK"}

@app.get("/health")
def health():
    return {"ok": True}
@app.get("/test")
def test():
    return {"test": "ok"}
