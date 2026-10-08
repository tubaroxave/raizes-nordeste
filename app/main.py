from fastapi import FastAPI
app = FastAPI(title="Raízes do Nordeste - API")

@app.get("/health")
def health():
    return {"status": "ok"}
