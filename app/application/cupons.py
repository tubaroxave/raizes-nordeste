from datetime import date
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session
from app.domain.errors import AppError
from app.domain.models import Cupom

def aplicar_cupom(db: Session, codigo: str, subtotal_centavos: int, cliente_id: int | None) -> int:
    #Devolve o desconto e usa o cupom
    cupom = db.scalar(select(Cupom).where(Cupom.codigo == codigo.strip().upper()))
    if cupom is None or not cupom.ativo or (cupom.usuario_id is not None and cupom.usuario_id != cliente_id):
        raise AppError(404, 'CUPOM_NAO_ENCONTRADO', "Cupom não encontrado.")
    if cupom.valido_ate < date.today():
        raise AppError(409, 'CUPOM_EXPIRADO, "Este cupom expirou.')
    consumo = db.execute(update(Cupom)
                         .where(Cupom.id == cupom.id, or_(Cupom.limite_usos.is_(None),
                                                          Cupom.usos < Cupom.limite_usos))
                                                          .values(usos=Cupom.usos +1))
    if consumo.rowcount != 1:
        raise AppError(409, 'CUPOM_ESGOTADO', "Este cupom já atingiu o limite de usos.")
    desconto = subtotal_centavos * cupom.valor // 100 if cupom.tipo == 'PERCENTUAL' else cupom.valor
    return min(desconto, subtotal_centavos)
