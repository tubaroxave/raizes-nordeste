from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.schemas import CardapioItemOut
from app.domain.models import CardapioItem, Unidade
from app.infraestrutura.database import get_db

router = APIRouter(prefix="/unidades", tags=["unidades"])

@router.get("/{unidade_id}/cardapio", response_model=list[CardapioItemOut])
def cardapio(unidade_id: int, db: Session = Depends(get_db)):
    unidade = db.get(Unidade, unidade_id)
    if not unidade or not unidade.ativa:
        raise HTTPException(404, "Unidade não encontrada.")
    itens = db.scalars(select(CardapioItem).where(CardapioItem.unidade_id == unidade_id)).all()
    return [CardapioItemOut(produto_id=i.produto_id, nome=i.produto.nome, categoria=i.produto.categoria, preco_centavos=i.preco_centavos, disponivel=i.disponivel) for i in itens]

