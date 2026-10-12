from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import SO_GESTAO
from app.api.schemas import Pagina, ProdutoAtualizaIn, ProdutoIn, ProdutoOut
from app.application.catalogo import produto_ou_404
from app.domain.errors import AppError
from app.domain.models import Produto
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/produtos', tags=['produtos'])

@router.get ('', response_model=Pagina[ProdutoOut])
def listar(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=50), categoria: str | None = None, db: Session = Depends(get_db)):
    filtro = select(Produto)
    total = db.scalar(select(func.count()).select_from(filtro.subquery()))
    produtos = db.scalars(filtro.order_by(Produto.id).offset((page - 1) * limit).limit(limit)).all()
    return Pagina[ProdutoOut](page=page, limit=limit, total=total, items=[ProdutoOut.model_validate(p) for p in produtos])

@router.get('/{produto_id}', response_model=ProdutoOut)
def obter(produto_id: int, db: Session = Depends(get_db)):
    return produto_ou_404(db, produto_id)

@router.post('', response_model=ProdutoOut, status_code=201, dependencies=[SO_GESTAO])
def criar(dados: ProdutoIn, db: Session = Depends(get_db)):
    if db.scalar(select(Produto).where(Produto.nome == dados.nome)):
        raise AppError(409, 'PRODUTO_JA_EXISTE', 'Já existe um produto com este nome.')
    produto = Produto(nome=dados.nome, categoria=dados.categoria.upper(), preco_base_centavos=dados.preco_base_centavos)

    db. add(produto)
    db.commit()
    db.refresh(produto)
    return produto

@router.put('/{produto_id}', response_model=ProdutoOut, dependencies=[SO_GESTAO])
def atualizar(produto_id: int, dados: ProdutoAtualizaIn, db: Session = Depends(get_db)):
    produto = produto_ou_404(db, produto_id, somente_ativo=False) # Pra poder reativar produto
    repetido = db.scalar(select(Produto).where(Produto.nome == dados.nome, Produto.id != produto_id))
    if repetido:
        raise AppError(409, 'PRODUTO_JA-EXISTE', "Já existe outro produto com esse nome.")

    produto.nome = dados.nome
    produto.categoria = dados.categoria.upper()
    produto.preco_base_centavos = dados.preco_base_centavos
    produto.ativo = dados.ativo
    db.commit
    db.refresh(produto)
    return produto

@router.delete('/{produto_id}', status_code=204, dependencies=[SO_GESTAO])
def excluir(produto_id: int, db: Session = Depends (get_db)):
    produto = produto_ou_404(db, produto_id)
    produto.ativo = False

    db.commit()