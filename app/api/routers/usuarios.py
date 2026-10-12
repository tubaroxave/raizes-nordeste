from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.api.deps import exigir, usuario_atual
from app.api.schemas import UsuarioEquipeIn, UsuarioOut, ConsentimentoIn, ConsentimentoOut
from app.domain.enums import Perfil
from app.domain.models import Usuario, Consentimento, Cupom
from app.infraestrutura.database import get_db
from app.infraestrutura.security import hash_senha
import secrets

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

@router.patch('/me/consentimentos', response_model=ConsentimentoOut)
def alterar_consentimento(dados: ConsentimentoIn, request: Request, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir(Perfil.CLIENTE))):
    registro = Consentimento(usuario_id=usuario.id, finalidade=dados.finalidade.value, aceito=dados.aceito, versao_termo=dados.versao_termo, ip=request.client.host if request.client else None)
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro
@router .delete('/me', status_code=204)
def excluir_minha_conta(db: Session = Depends(get_db), usuario: Usuario = Depends(exigir(Perfil.CLIENTE))):
    #Pedidos ficam no histórico mas sem dado pessoal. (O exato contrário que todas as empresas atuais fazem, cof cof, Google.)
    usuario.nome = 'Usuário removido'
    usuario.email = f'removido-{usuario.id}@anonimo.invalid'
    usuario.senha_hash = hash_senha(secrets.token_urlsafe(32))
    usuario.ativo = False
    for consentimento in db.scalars(select(Consentimento).where(Consentimento.usuario_id == usuario.id)):
        consentimento.ip = None
    db.execute(update(Cupom).where(Cupom.usuario_id == usuario.id).values(ativo=False))
    db.commit()
