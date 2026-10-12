from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import SO_GESTAO
from app.api.schemas import CupomIn, CupomOut
from app.domain.enums import TipoCupom
from app.domain.errors import AppError
from app.domain.models import Cupom
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/cupons', tags=['cupons'], dependencies = [SO_GESTAO])

@router.post('', response_model=CupomOut, status_code=201)
def criar(dados: CupomIn, db: Session = Depends(get_db)):
    codigo = dados.codigo.strip().upper()
    if db.scalar(select(Cupom).where(Cupom.codigo == codigo)):
        raise AppError(409, 'CUPOM_JA_EXISTE', "Já existe um cupom com este código.")
    if dados.tipo == TipoCupom.PERCENTUAL and dados.valor > 100:
        raise AppError(422, 'VALIDACAO_FALHOU', "Cupom percentual aceita apenas valor de 1 a 100. PERCENTUAL", [{'field': 'valor', 'issue': 'máximo de 100 para PERCENTUAL'}])
    cupom = Cupom(codigo=codigo, tipo=dados.tipo.value, valor=dados.valor, valido_ate=dados.valido_ate, limite_usos=dados.limite_usos)
    db.add(cupom)
    db.commit()
    db.refresh(cupom)
    return cupom