from fastapi import FastAPI
from app.api.routers import auth, unidades, usuarios
from app.domain import models
from app.infraestrutura.database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Raízes do Nordeste - API")
app.include_router(unidades.router)
app.include_router(auth.router)
app.include_router(usuarios.router)


@app.get("/health")
def health():
    return {"status": "ok"}



