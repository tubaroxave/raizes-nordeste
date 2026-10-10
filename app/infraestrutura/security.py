from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

from app.config import ACCESS_TOKEN_MINUTES, JWT_SECRET

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
def conferir_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.hashpw(senha.encode(), senha_hash.encode())

def criar_token(usuario_id: int, perfil: str) -> str:
    agora = datetime.now(timezone.utc)
    dados = {"sub": str(usuario_id), "perfil": perfil, "iat": agora, "exp": agora + timedelta(minutes=ACCESS_TOKEN_MINUTES)}
    return jwt.encode(dados, JWT_SECRET, algorithm="HS256")

def decodificar_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

