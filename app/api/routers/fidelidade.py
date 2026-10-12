from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import exigir
from app.api.schemas import CupomOut, ResgateIn, SaldoOut
from app.application.fidelidade import resgatar_pontos, saldo_pontos, tem_consentimento
from app.domain.enums import Perfil
from app.domain.models import Usuario
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/fidelidade', tags=['fidelidade'])

@router.get('/saldo', response_model=SaldoOut)
def saldo(db: Session = Depends(get_db), usuario: Usuario = Depends(exigir(Perfil.CLIENTE))):
    return SaldoOut(pontos=saldo_pontos(db,usuario.id), consentimento_fidelidade=tem_consentimento(db,usuario.id))

@router.post('/resgates', response_model=CupomOut, status_code=201)
def resgatar(dados: ResgateIn, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir(Perfil.CLIENTE))):
    cupom = resgatar_pontos(db, usuario.id, dados.pontos)
    db.commit()
    db.refresh(cupom)
    return cupom
