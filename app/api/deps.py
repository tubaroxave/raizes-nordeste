import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.domain.enums import Perfil
from app.domain.errors import AppError
from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.infraestrutura.security import decodificar_token

bearer = HTTPBearer (auto_error = False, description='Cole o Token retornado por POST /auth/login')

def usuario_atual(cred: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Usuario:
    if cred is None:
        raise AppError(401, 'TOKEN_AUSENTE', "Token de acesso ausente.")
    try:
        dados = decodificar_token(cred.credentials)
    except jwt.PyJWTError:
        raise AppError(401, 'TOKEN_INVALIDO', "Token inválido ou expirado.")
    usuario = db.get(Usuario, int(dados['sub']))
    if not usuario or not usuario.ativo:
        raise AppError(401, 'USUARIO_INATIVO', "Usuário inexistente ou inativo.")
    return usuario

def exigir(*perfis):
    permitidos = {p.value for p in perfis}

    def dependencia(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in permitidos:
            raise AppError(403, 'SEM_PERMISSAO', "Seu perfil não tem permissão para este recurso.")
        return usuario
    return dependencia

#ATALHOS (Que eu deveria ter pensado logo de cara talvez.)
SO_GESTAO = Depends(exigir(Perfil.GERENTE, Perfil.ADMIN))
EQUIPE = Depends(exigir(Perfil.ATENDENTE, Perfil.COZINHA, Perfil.GERENTE, Perfil.ADMIN))
QUEM_PEDE = Depends(exigir(Perfil.CLIENTE, Perfil.ATENDENTE, Perfil.GERENTE, Perfil.ADMIN))
