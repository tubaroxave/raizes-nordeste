from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import SO_GESTAO
from app.api.schemas import CardapioItemIn, CardapioItemOut, UnidadeOut, UnidadeIn
from app.application.catalogo import produto_ou_404, unidade_ou_404
from app.domain.models import CardapioItem, Produto, Unidade
from app.infraestrutura.database import get_db

router = APIRouter(prefix='/unidades', tags=['unidades'])

def para_saida(item: CardapioItem) -> CardapioItemOut:
    return CardapioItemOut(produto_id=item.produto_id, nome=item.produto.nome, categoria=item.produto.categoria, preco_centavos=item.preco_centavos, disponivel=item.disponivel)

@router.get('', response_model=list[UnidadeOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Unidade).where(Unidade.ativa.is_(True)).order_by(Unidade.id)).all()

@router.post('', response_model=UnidadeOut, status_code=201, dependencies=[SO_GESTAO])
def criar_unidade(dados: UnidadeIn, db: Session = Depends(get_db)):
    unidade = Unidade(
        nome=dados.nome,
        cidade=dados.cidade,
        uf=dados.uf.upper()
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade

@router.get('/{unidade_id}/cardapio', response_model=list[CardapioItemOut])
def cardapio(unidade_id: int, db: Session = Depends(get_db)):
    unidade_ou_404(db, unidade_id)
    items = db.scalars(

        select(CardapioItem)
        .join(Produto)
        .where(
            CardapioItem.unidade_id == unidade_id,
            Produto.ativo.is_(True)
        )
        .order_by(CardapioItem.id)
    )   .all()
    return [para_saida(item) for item in items]
        
    
@router.put ('/{unidade_id}/cardapio/{produto_id}', response_model=CardapioItemOut, dependencies=[SO_GESTAO])
def definir_item_do_cardapio(unidade_id: int, produto_id: int, dados: CardapioItemIn, db: Session = Depends(get_db)):
    unidade_ou_404(db, unidade_id)
    produto_ou_404(db, produto_id)
    item = db.scalar(select(CardapioItem).where(CardapioItem.unidade_id == unidade_id, CardapioItem.produto_id == produto_id))
    if item is None:
        item = CardapioItem(unidade_id=unidade_id, produto_id=produto_id, preco_centavos=dados.preco_centavos, disponivel=dados.disponivel)
        db.add(item)
    else: item.preco_centavos = dados.preco_centavos
    item.disponivel = dados.disponivel
    db.commit()
    db.refresh(item)
    return para_saida(item)