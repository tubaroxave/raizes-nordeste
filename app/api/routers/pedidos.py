from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import EQUIPE, QUEM_PEDE, usuario_atual, ip_do_cliente
from app.api.schemas import Pagina, PedidoIn, PedidoOut, StatusIn
from app.application.pedidos import buscar_pedido, criar_pedido, cancelar_pedido
from app.domain.enums import CanalPedido, Perfil, StatusPedido
from app.domain.models import Pedido, Usuario
from app.infraestrutura.database import get_db
from app.domain.maquina_estados import validar_mudanca_manual
from app.application.auditoria import registrar


router = APIRouter(prefix='/pedidos', tags=['pedidos'])
@router.post('', response_model=PedidoOut, status_code=201)
def criar(
    dados: PedidoIn, 
    request: Request, 
    db: Session = Depends(get_db), 
    usuario: Usuario = QUEM_PEDE
    ):
    items: dict[int, int] = {}

    for item in dados.itens:
        items[item.produto_id] = (
            items.get(item.produto_id, 0) + item.quantidade
            )
        
    cliente_id = (
        usuario.id if usuario.perfil == Perfil.CLIENTE.value else None
        )
    pedido = criar_pedido(
            db, 
            unidade_id=dados.unidade_id, 
            canal=dados.canal_pedido.value, 
            items = items, 
            cliente_id=cliente_id, 
            cupom_codigo=dados.cupom_codigo)
    registrar(
            db,
            acao='PEDIDO_CRIADO',
            entidade='pedido',
            entidade_id=pedido.id,
            usuario_id=usuario.id,
            detalhe=(
                f'canal={dados.canal_pedido.value};'
                f'total={pedido.total_centavos}'
            ),
            ip=ip_do_cliente(request)
        )
        
    db.commit()
    db.refresh(pedido)
    return PedidoOut.model_validate(pedido)

@router.get('', response_model=Pagina[PedidoOut])
def listar(canal_pedido: CanalPedido | None = Query(None, alias='canalPedido'),
           status: StatusPedido | None = None,
           unidade_id: int | None = Query(None, alias='unidadeId'),
           page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50),
           db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    filtro = select(Pedido)
    if usuario.perfil == Perfil.CLIENTE.value:
        filtro = filtro.where(Pedido.cliente_id == usuario.id)
    if canal_pedido:
        filtro = filtro.where(Pedido.canal_pedido == canal_pedido.value)
    if status:
        filtro = filtro.where(Pedido.status == status.value)
    if unidade_id:
        filtro = filtro.where(Pedido.unidade_id == unidade_id)
    total = db.scalar(select(func.count()).select_from(filtro.subquery()))
    pedidos = db.scalars(
        filtro
        .order_by(Pedido.id.desc())
        .offset((page - 1)* limit)
        .limit(limit)
    ).all()
    return Pagina[PedidoOut](page=page, limit=limit, total=total, items=[PedidoOut.model_validate(p) for p in pedidos])


@router.get('/{pedido_id}', response_model=PedidoOut)
def obter(pedido_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    return PedidoOut.model_validate(buscar_pedido(db, pedido_id, usuario))


@router.patch('/{pedido_id}/status', response_model=PedidoOut)
def mudar_status(
    pedido_id: int,
    dados: StatusIn,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = EQUIPE
):
    pedido = buscar_pedido(db, pedido_id, usuario)
    status_anterior = pedido.status
    validar_mudanca_manual(
        pedido.status, dados.status.value, usuario.perfil
    )

    pedido.status = dados.status.value

    registrar(
        db,
        acao='STATUS_ALTERADO',
        entidade='pedido',
        entidade_id=pedido.id,
        usuario_id=usuario.id,
        detalhe=(
            f'{status_anterior} -> {pedido.status}'
        
        ),
        ip=ip_do_cliente(request)
    )
    db.commit()
    db.refresh(pedido)
    return PedidoOut.model_validate(pedido)

@router.post('/{pedido_id}/cancelar', response_model=PedidoOut)
def cancelar(
    pedido_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = QUEM_PEDE
):
    pedido = buscar_pedido(db, pedido_id, usuario)
    status_anterior = pedido.status
    cancelar_pedido(db, pedido, usuario)
    registrar(
        db,
        acao='PEDIDO_CANCELADO',
        entidade='pedido',
        entidade_id=pedido.id,
        usuario_id=usuario.id,
        detalhe=f'{status_anterior} -> {pedido.status}',
        ip=ip_do_cliente(request)
    )

    db.commit()
    db.refresh(pedido)
    return PedidoOut.model_validate(pedido)
