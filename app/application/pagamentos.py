from sqlalchemy.orm import Session
from app.domain.errors import AppError
from app.domain.maquina_estados import TRANSICOES, validar_transicao
from app.domain.models import Pagamento, Pedido
from app.infraestrutura import gateway_pagamento
from app.infraestrutura.gateway_pagamento import GatewayTimeout

MAX_TENTATIVAS = 2

def pagar_pedido(db: Session, pedido: Pedido, metodo: str, simular: str) -> Pagamento:
    #O pedido só é pago se ele vai pra PAGO na maquina de estados.
    if 'PAGO' not in TRANSICOES[pedido.status]:
        raise AppError(409, 'PEDIDO_NAO_PAGAVEL', f'Um pedido com status {pedido.status} não aceita pagamento.')
    resposta = None
    for tentativas in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = gateway_pagamento.gateway.cobrar(pedido.total_centavos, metodo, simular, tentativas)
            break
        except GatewayTimeout:
            continue
    base = dict(pedido_id=pedido.id, metodo=metodo, valor_centavos=pedido.total_centavos, tentativas=tentativas)
    if resposta is None:
        pagamento = Pagamento(status='ERRO_GATEWAY', payload={'erro': 'timeout'}, **base)
        db.add(pagamento)
        return pagamento
    novo_status = 'PAGO' if resposta['status'] == 'APROVADO' else 'PAGAMENTO_RECUSADO'
    validar_transicao(pedido.status, novo_status)
    pagamento = Pagamento(status=resposta['status'], transacao_id=resposta['transacaoId'], payload=resposta, **base)
    db.add(pagamento)
    pedido.status = novo_status
    return pagamento
