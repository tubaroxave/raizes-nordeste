from sqlalchemy import update
from sqlalchemy.orm import Session
from app.domain.errors import AppError
from app.domain.models import Estoque, MovimentoEstoque

def registrar_entrada(db: Session, unidade_id: int, produto_id: int, quantidade: int, motivo: str, usuario_id: int | None = None) -> None:

    resultado = db.execute(
        update(Estoque)
        .where(Estoque.unidade_id == unidade_id, Estoque.produto_id == produto_id)
        .values(quantidade=Estoque.quantidade + quantidade)
    )
    if resultado.rowcount == 0:

        db.add(Estoque(unidade_id=unidade_id, produto_id=produto_id, quantidade=quantidade))
    db.add(MovimentoEstoque(unidade_id=unidade_id, produto_id=produto_id, tipo='ENTRADA', quantidade=quantidade, motivo=motivo, usuario_id=usuario_id))

def registrar_saida(db: Session, unidade_id: int, produto_id: int, quantidade: int, motivo: str, usuario_id: int | None = None) -> None:
    resultado = db.execute(
        update(Estoque)
        .where(Estoque.unidade_id == unidade_id, Estoque.produto_id == produto_id,
               Estoque.quantidade >= quantidade)
        .values(quantidade=Estoque.quantidade - quantidade)
    )

    if resultado.rowcount !=1:
        raise AppError(409, 'ESTOQUE_INSUFICIENTE', 'Saldo insuficiente para essa saida.', [{'field': 'produtoId', 'issue': f'saldo insuficiente para o produto {produto_id}'}])
    db.add(MovimentoEstoque(unidade_id=unidade_id, produto_id=produto_id, tipo='SAIDA', quantidade=quantidade, motivo=motivo, usuario_id=usuario_id))

    