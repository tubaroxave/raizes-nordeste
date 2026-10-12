from app.domain.errors import AppError
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from app.config import ACCESS_TOKEN_MINUTES
from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.infraestrutura.security import conferir_senha, criar_token, hash_senha
from app.application.auditoria import registrar as registrar_auditoria
from app.api.deps import ip_do_cliente

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UsuarioOut, status_code=201)
def registrar(dados: RegistroIn, db: Session = Depends(get_db)):
    if not dados.aceite_termos:
        raise AppError(422, 'TERMOS_NAO_ACEITOS', "É preciso aceitar os termos de uso.")
    email = dados.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise AppError(409, 'EMAIL_JA_CADASTRADO', "Esse email já foi cadastrado.")
    usuario = Usuario(nome=dados.nome, email=email, senha_hash=hash_senha(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
    
@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, request: Request, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == dados.email.lower()))
    if not usuario or not usuario.ativo or not conferir_senha(dados.senha, usuario.senha_hash):
        registrar_auditoria(
            db,
            acao='LOGIN_FALHO',
            entidade='usuario',
            usuario_id=usuario.id if usuario else None,
            detalhe='credenciais inválidas',
            ip=ip_do_cliente(request)
        )
        raise AppError(401, 'CREDENCIAIS_INVALIDAS', "Email ou senha inválidos.")
    return TokenOut(access_token=criar_token(usuario.id, usuario.perfil), expires_in=ACCESS_TOKEN_MINUTES * 60, user=UsuarioOut.model_validate(usuario))
