from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import exigir
from app.api.schemas import AuditoriaOut, Pagina
from app.domain.enums import Perfil
from app.domain.models import AuditLog
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/auditoria', tags=['auditoria'], dependencies = [Depends(exigir(Perfil.ADMIN))])

@router.get('', response_model=Pagina[AuditoriaOut])
def listar(acao: str | None = None, entidade: str | None = None,
           usuario_id: int | None = Query(None, alias='UsuarioId'),
        page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    filtro = select(AuditLog)
    if acao:
        filtro = filtro.where(AuditLog.acao == acao.upper())
    if entidade:
        filtro = filtro.where(AuditLog.entidade == entidade.lower())
    if usuario_id:
        filtro = filtro.where(AuditLog.usuario_id == usuario_id)
    total = db.scalar(select(func.count()).select_from(filtro.subquery()))
    logs = db.scalars(filtro.order_by(AuditLog.id.desc()).offset((page - 1) * limit).limit(limit)).all()
    return Pagina[AuditoriaOut](page=page, limit=limit, total=total, items=[AuditoriaOut.model_validate(x) for x in logs])
