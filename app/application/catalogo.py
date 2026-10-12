from sqlalchemy.orm import Session
from app.domain.errors import AppError
from app.domain.models import Produto, Unidade

def unidade_ou_404(db: Session, unidade_id: int) -> Unidade:
    unidade = db.get(Unidade, unidade_id)
    if unidade is None or not unidade.ativa:
        raise AppError(404, 'UNIDADE_NAO_ENCONTRADA', "Unidade não encontrada.")
    return unidade

def produto_ou_404(db:Session, produto_id: int, somente_ativo: bool = True) -> Produto:
    produto = db.get(Produto, produto_id)
    if produto is None or (somente_ativo and not produto.ativo):
        raise AppError (404, 'PRODUTO_NAO_ENCONTRADO', "Produto não encontrado.")
    return produto