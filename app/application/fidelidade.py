import secrets
from datetime import date, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain.errors import AppError
from app.domain.models import Consentimento, Cupom, Pedido, PontosMovimento

FINALIDADE = 'FIDELIDADE'
CENTAVOS_POR_PONTO = 5 #Aí 100 pontos viram R$5.00

def tem_consentimento(db: Session, usuario_id: int) -> bool:
    ultimo = db.scalar(select(Consentimento).where(Consentimento.usuario_id== usuario_id, Consentimento.finalidade == FINALIDADE).order_by(Consentimento.id.desc()).limit(1))
    return bool (ultimo and ultimo.aceito)

def saldo_pontos(db: Session, usuario_id: int) -> int:
    return db.scalar(select(func.coalesce(func.sum(PontosMovimento.pontos), 0)).where(PontosMovimento.usuario_id == usuario_id))

def acumular_pontos(db: Session, pedido: Pedido) -> int:
    #1 ponto por real. Sem cliente ou sem consentimento não acumula pontos.
    if pedido.cliente_id is None or not tem_consentimento(db, pedido.cliente_id):
        return 0
    pontos = pedido.total_centavos // 100
    if pontos > 0:
        db.add(PontosMovimento(usuario_id=pedido.cliente_id, pontos=pontos, movito=f'Pedido #{pedido.id} pago', pedido_id=pedido.id))
        return pontos

def resgatar_pontos(db: Session, usuario_id: int, pontos: int) -> Cupom:
    if not tem_consentimento(db, usuario_id):
        raise AppError(403, "CONSENTIMENTO_NECESSARIO", "É preciso aceitar o programa de fidelidade para resgatar pontos.")
    if pontos % 100 !=0:
        raise AppError(422, 'VALIDACAO_FALHOU', "O resgate é feito em múltiplos de 100 pontos.", [{'field': 'pontos', 'issue': 'use múltiplos de 100'}])
    if saldo_pontos(db, usuario_id) < pontos:
        raise AppError(409, 'PONTOS_INSUFICIENTES', "Saldo de pontos insuficiente")

    db.add(PontosMovimento(usuario_id=usuario_id, pontos=-pontos, motivo='Resgate de pontos'))
    cupom = Cupom(codigo =f'PTS-{secrets.token_hex(4).upper()}', tipo='FIXO', valor=pontos * CENTAVOS_POR_PONTO, valido_ate=date.today() + timedelta(days=30), limite_usos=1, usuario_id=usuario_id)
    db.add(cupom)
    return cupom