from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import EQUIPE, SO_GESTAO
from app.api.schemas import EstoqueOut, MovimentoIn
from app.application.catalogo import produto_ou_404, unidade_ou_404
from app.application.estoque import registrar_entrada, registrar_saida
from app.domain.enums import TipoMovimento
from app.domain.models import Estoque, Produto, Usuario
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/estoque', tags=['estoque'])

@router.get('/unidades/{unidade_id}', response_model=list[EstoqueOut], dependencies=[EQUIPE])
def saldo_da_unidade(unidade_id: int, db: Session = Depends(get_db)):
    unidade_ou_404(db, unidade_id)
    linhas = db.execute(
        select(Estoque, Produto.nome).join(Produto, Produto.id == Estoque.produto_id)
        .where(Estoque.unidade_id == unidade_id).order_by(Estoque.produto_id)).all()
    return [EstoqueOut(unidade_id=e.unidade_id, produto_id=e.produto_id, nome=nome, quantidade=e.quantidade) 
            for e, nome in linhas]

@router.post('/movimentos', response_model=EstoqueOut, status_code=201)
def movimentar(dados: MovimentoIn, db: Session = Depends(get_db), usuario:Usuario = SO_GESTAO):
    unidade_ou_404(db, dados.unidade_id)
    produto = produto_ou_404(db, dados.produto_id)
    if dados.tipo == TipoMovimento.ENTRADA:
        registrar_entrada(db, dados.unidade_id, dados.produto_id, dados.quantidade, dados.motivo, usuario.id)
    else:
        registrar_saida(db, dados.unidade_id, dados.produto_id, dados.quantidade, dados.motivo, usuario.id)

    db.commit()
    saldo = db.scalar(
        select(Estoque.quantidade).where(
            Estoque.unidade_id == dados.unidade_id,
            Estoque.produto_id == dados.produto_id
        )
    )
    return EstoqueOut(
        unidade_id=dados.unidade_id,
        produto_id=dados.produto_id,
        nome=produto.nome,
        quantidade=saldo
    )