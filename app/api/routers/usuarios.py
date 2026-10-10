from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import exigir, usuario_atual
from app.api.schemas import UsuarioEquipeIn, UsuarioOut
from app.domain.enums import Perfil
from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.infraestrutura.security import hash_senha

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("/me", response_model=UsuarioOut)
def meu_perfil(usuario: Usuario = Depends(usuario_atual)):
    return usuario

@router.post("", response_model=UsuarioOut, status_code=201)
def criar_usuario_da_equipe(dados: UsuarioEquipeIn, db: Session = Depends(get_db), _admin: Usuario = Depends(exigir(Perfil.ADMIN))):
    email = dados.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "Já existe um usuário com esse e-mail.")
    usuario = Usuario(nome=dados.nome, email=email, senha_hash=hash_senha(dados.senha), perfil=dados.perfil.value)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario