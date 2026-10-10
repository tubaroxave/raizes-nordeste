from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from app.config import ACCESS_TOKEN_MINUTES
from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.infraestrutura.security import conferir_senha, criar_token, hash_senha

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UsuarioOut, status_code=201)
def registrar(dados: RegistroIn, db: Session = Depends(get_db)):
    if not dados.aceite_termos:
        raise HTTPException(422, "É preciso aceitar os termos de uso.")
    email = dados.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(409, "Esse email já foi cadastrado.")
    usuario = Usuario(nome=dados.nome, email=email, senha_hash=hash_senha(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
    
@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == dados.email.lower()))
    if not usuario or not usuario.ativo or not conferir_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(401,"Email ou senha inválidos.")
    return TokenOut(access_token=criar_token(usuario.id, usuario.perfil), expires_in=ACCESS_TOKEN_MINUTES * 60, user=UsuarioOut.model_validate(usuario))
