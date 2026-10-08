from fastapi import FastAPI
from app.api.routers import unidades
from app.domain import models
from app.infraestrutura.database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Raízes do Nordeste - API")
app.include_router(unidades.router)

@app.get("/health")
def health():
    return {"status": "ok"}
