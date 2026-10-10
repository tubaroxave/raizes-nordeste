from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infraestrutura.database import Base
from app.domain.enums import Perfil

class Unidade(Base):
    __tablename__ = "unidades"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    cidade: Mapped[str] = mapped_column(String(60))
    uf: Mapped[str] = mapped_column(String(2))
    ativa: Mapped[bool] = mapped_column(default=True)

class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    categoria: Mapped[str] = mapped_column(String(30))
    preco_base_centavos: Mapped[int]
    ativo: Mapped[bool] = mapped_column(default=True)
    __table_args__ = (CheckConstraint("preco_base_centavos >= 0", name="ck_produto_preco"),)

class CardapioItem(Base):
    """PREÇO E DISPONIBILIDADE de um produto em UMA unidade"""
    __tablename__ = "cardapio_itens"
    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    preco_centavos: Mapped[int]
    disponivel: Mapped[bool] = mapped_column(default=True)
    produto: Mapped[Produto] = relationship()
    __table_args__ = (UniqueConstraint("unidade_id","produto_id", name="uq_cardapio_unidade_produto"), CheckConstraint("preco_centavos >= 0", name="ck_cardapio_preco"))
                                                                                                                   
class Estoque(Base):
    """SALDO de um produto em UMA unidade"""
    __tablename__ = "estoque"
    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    quantidade: Mapped[int] = mapped_column(default=0)
    __table_args__ = (UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"), CheckConstraint("quantidade >= 0", name="ck_estoque_quantidade"))


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[str] = mapped_column(String(10), default=Perfil.CLIENTE.value)
    ativo: Mapped[bool] = mapped_column(default=True)
    