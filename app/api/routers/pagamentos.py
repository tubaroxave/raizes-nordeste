from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import QUEM_PEDE, ip_do_cliente
from app.api.schemas import PagamentoIn, PagamentoOut
from app.application.pagamentos import pagar_pedido
from app.application.pedidos import buscar_pedido
from app.domain.errors import AppError
from app.domain.models import Usuario
from app.infraestrutura.database import get_db
from app.application.auditoria import registrar

router = APIRouter(prefix='/pagamentos', tags = ['pagamentos'])

@router.post('', response_model=PagamentoOut, status_code=201)
def pagar(dados: PagamentoIn, request: Request, db: Session = Depends(get_db), usuario: Usuario = QUEM_PEDE):
    pedido = buscar_pedido(db, dados.pedido_id, usuario)
    pagamento = pagar_pedido(db, pedido, dados.metodo.value, dados.simular.value)
    registrar(
        db,
        acao=('PAGAMENTO_ERRO_GATEWAY') 
        if pagamento.status == "ERRO_GATEWAY"
        else(
            'PAGAMENTO_APROVADO'
            if pagamento.status == "APROVADO"
            else 'PAGAMENTO_RECUSADO'

        ),
        entidade='pagamento',
        entidade_id=pagamento.id,
        usuario_id=usuario.id,
        detalhe=(f'metodo={pagamento.metodo}; '
                 f'tentativas={pagamento.tentativas}'),
                 ip = ip_do_cliente(request)
    )

    db.commit()
    if pagamento.status == 'ERRO_GATEWAY':
        raise AppError(502, 'GATEWAY_INDISPONIVEL', 'O serviço de pagamento não respondeu. Tente novamente em instantes.')
    db.refresh(pedido)
    return PagamentoOut(id=pagamento.id, pedido_id=pedido.id, status=pagamento.status, metodo=pagamento.metodo, valor_centavos=pagamento.valor_centavos, transacao_id=pagamento.transacao_id, tentativas=pagamento.tentativas, pedido_status=pedido.status)