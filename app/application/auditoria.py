from sqlalchemy.orm import Session
from app.domain.models import AuditLog

def registrar(
        db,
        acao,
        entidade,
        entidade_id=None,
        usuario_id=None,
        detalhe=None,
        ip=None
):
    db.add(AuditLog(
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        usuario_id=usuario_id,
        detalhe=detalhe[:45] if detalhe else None
    ))