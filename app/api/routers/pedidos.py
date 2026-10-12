from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import QUEM_PEDE, usuario_atual
from app.api.schemas import Pagina, PedidoIn, PedidoOut
from app.application.pedidos import buscar_pedido, criar_pedido
from app.domain.enums import CanalPedido, Perfil, StatusPedido
from app.domain.models import Pedido, Usuario
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/pedidos', tags=['pedidos'])
@router.post('', response_model=PedidoOut, status_code=201)
def criar(dados: PedidoIn, db: Session = Depends(get_db), usuario: Usuario = QUEM_PEDE):
    items: dict[int, int] = {}
    for item in dados.itens:
        items[item.produto_id] = items.get(item.produto_id, 0) + item.quantidade
        cliente_id = usuario.id if usuario.perfil == Perfil.CLIENTE.value else None
        pedido = criar_pedido(db, unidade_id=dados.unidade_id, canal=dados.canal_pedido.value, items = items, cliente_id=cliente_id)
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
    pedidos = db.scalars(filtro.order_by(Pedido.id.desc())).offset((page - 1) * limit).limit(limit).all()
    return Pagina[PedidoOut](page=page, limit=limit, total=total, items=[PedidoOut.model_validate(p) for p in pedidos])


@router.get('/{pedido_id}', response_model=PedidoOut)
def obter(pedido_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    return PedidoOut.model_validate(buscar_pedido(db, pedido_id, usuario))