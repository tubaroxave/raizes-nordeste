from sqlalchemy import select
from sqlalchemy.orm import Session
from app.application.catalogo import unidade_ou_404
from app.application.estoque import registrar_saida
from app.domain.enums import Perfil
from app.domain.errors import AppError
from app.domain.models import CardapioItem, Pedido, PedidoItem, Usuario
from app.application.estoque import registrar_entrada, registrar_saida
from app.domain.maquina_estados import validar_transicao
from app.application.cupons import aplicar_cupom

def buscar_pedido(db: Session, pedido_id: int, usuario: Usuario) -> Pedido:
    pedido = db.get(Pedido, pedido_id)
    if pedido is None or (usuario.perfil == Perfil.CLIENTE.value and pedido.cliente_id != usuario.id):
        raise AppError(404, 'PEDIDO_NAO_ENCONTRADO', 'Pedido não encontrado.')
    return pedido

def criar_pedido(db: Session, *, unidade_id: int, canal: str, items: dict[int, int],
                 cliente_id: int | None, cupom_codigo= str | None) -> Pedido:
    unidade_ou_404(db,unidade_id)
    pedido = Pedido(
        unidade_id=unidade_id,
        cliente_id=cliente_id,
        canal_pedido=canal,
        
    )
    db.add(pedido)
    db.flush()

    subtotal = 0

    for produto_id in sorted(items):
        quantidade = items[produto_id]
        detalhe = [
            {'field': 'produtoId', 'issue': f'produto {produto_id}'}
        ]

    no_cardapio = db.scalar(
        select(CardapioItem).where(
            CardapioItem.unidade_id == unidade_id,
            CardapioItem.produto_id == produto_id
        )
    )

    if no_cardapio is None or not no_cardapio.produto.ativo:
        raise AppError(
            404,
            'ITEM_FORA_DO_CARDAPIO',
            'Produto fora do cardápio desta unidade.',
            detalhe
        )

    if not no_cardapio.disponivel:
        raise AppError(
            409,
            'ITEM_INDISPONIVEL',
            'Produto indisponível nessa unidade.',
            detalhe
        )

    registrar_saida(
        db,
        unidade_id,
        produto_id,
        quantidade,
        f'Pedido#{pedido.id}'
    )

    preco_unitario = no_cardapio.preco_centavos

    pedido.itens.append(
        PedidoItem(
            produto_id=produto_id,
            quantidade=quantidade,
            preco_unitario_centavos=preco_unitario
        )
    )

    subtotal += preco_unitario * quantidade

    desconto = aplicar_cupom(db, cupom_codigo, subtotal, cliente_id) if cupom_codigo else 0
    pedido.subtotal_centavos = subtotal
    pedido.desconto_centavos = desconto
    pedido.cupom_codigo = cupom_codigo.strip().upper() if cupom_codigo else None
    pedido.total_centavos = subtotal - desconto

    return pedido


def cancelar_pedido(db: Session, pedido: Pedido, usuario: Usuario) -> None:
    if usuario.perfil == Perfil.CLIENTE.value and pedido.status not in ('AGUARDANDO_PAGAMENTO', "PAGAMENTO_RECUSADO"):
        raise AppError(403, 'CANCELAMENTO_NAO_PERMITIDO', 'Depois do pagamento, só a equipe pode cancelar o pedido.')
    validar_transicao(pedido.status, 'CANCELADO')
    for item in pedido.itens:
        registrar_entrada(db, pedido.unidade_id, item.produto_id, item.quantidade, f'Cancelamento do pedido #{pedido.id}', usuario.id)
        pedido.status = 'CANCELADO'