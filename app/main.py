from fastapi import FastAPI
from app.api.errors import registrar_handlers
from app.api.routers import auth, produtos, unidades, usuarios, estoque
from app.domain import models
from app.infraestrutura.database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI(title='Raízes do Nordeste - API')
registrar_handlers(app)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(estoque.router)

@app.get('/health')
def health():
    return {'status': 'ok'}