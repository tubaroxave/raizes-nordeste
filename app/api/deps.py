import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.infraestrutura.security import decodificar_token

bearer = HTTPBearer(auto_error=False, description="Cole o accessToken retornado por POST /auth/login")

def usuario_atual(cred:HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> Usuario:
    if cred is None:
        raise HTTPException(401, "Token de acesso ausente.")
    try:
        dados = decodificar_token(cred.credentials)
    except jwt.PyJWTError:
        raise HTTPException(401, "Token de acesso inválido ou expirado.")
    usuario = db.get(Usuario, int(dados["sub"]))
    if not usuario or not usuario.ativo:
        raise HTTPException(401, "Usuário inexistente ou inativo.")
    return usuario

def exigir(*perfis):
    permitidos = {p.value for p in perfis}
    def dependencia(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        if usuario.perfil not in permitidos:
            raise HTTPException(403, "Perfil de usuário não autorizado")
        return usuario

    return dependencia