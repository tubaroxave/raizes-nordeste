from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infraestrutura.database import Base
from app.domain.enums import Perfil, StatusPedido
from datetime import date, datetime, timezone

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

def agora() -> datetime:
    return datetime.now(timezone.utc)


#Histórico do estoque...
class MovimentoEstoque(Base):
    __tablename__ = 'movimentos_estoque'
    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey('unidades.id'))
    produto_id: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    tipo: Mapped[str] = mapped_column(String(10))
    quantidade: Mapped[int]
    motivo: Mapped[str] = mapped_column(String(120))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuarios.id'))
    criado_em: Mapped[datetime] = mapped_column(default=agora)
    __table_args__ = (CheckConstraint('quantidade > 0', name='ck_movimento_quantidade'),)
    
class Pedido(Base):
    __tablename__ = 'pedidos'
    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey('unidades.id'))
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"),
        nullable=True
    )
    canal_pedido: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(25), default=StatusPedido.AGUARDANDO_PAGAMENTO.value)
    subtotal_centavos: Mapped[int] = mapped_column(default=0)
    desconto_centavos: Mapped[int] = mapped_column(default=0)
    total_centavos: Mapped[int] = mapped_column(default=0)
    cupom_codigo: Mapped[str | None] = mapped_column(String(30))
    criado_em: Mapped[datetime] = mapped_column(default=agora, onupdate=agora)

    itens: Mapped[list["PedidoItem"]] = relationship(cascade='all, delete-orphan', order_by='PedidoItem.id')
    __table_args__ = (CheckConstraint('total_centavos >= 0', name='ck_pedido_total'),)

class PedidoItem(Base):
    __tablename__ = 'pedido_itens'

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey('pedidos.id'))
    produto_id: Mapped[int] = mapped_column(ForeignKey('produtos.id'))
    quantidade: Mapped[int]
    preco_unitario_centavos: Mapped[int]

    produto: Mapped[Produto] = relationship()

    __table_args__=(CheckConstraint('quantidade > 0', name='ck_item_quantidade'),)

    @property
    def nome(self) -> str:
        return self.produto.nome

    @property
    def subtotal_centavos(self) -> int:
        return self.quantidade * self.preco_unitario_centavos


class Pagamento(Base):
    __tablename__ = 'pagamentos'

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey('pedidos.id'))
    metodo: Mapped[str] = mapped_column(String(20))
    valor_centavos: Mapped[int]
    status: Mapped[str] = mapped_column(String(15)) #APROVADO, RECUSADO OU ERRO_GATEWAY
    transacao_id: Mapped[str | None] = mapped_column(String(60))
    tentativas: Mapped[int] = mapped_column(default=1)
    payload: Mapped[dict] = mapped_column(JSON) #resposta do gateway
    criado_em: Mapped[datetime] = mapped_column(default=agora)
#LGPD
class Consentimento(Base):
    __tablename__ = 'consentimentos'

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    finalidade: Mapped[str] = mapped_column(String(30))
    aceito: Mapped[bool]
    versao_termo: Mapped[str] = mapped_column(String(10))
    ip: Mapped[str | None] = mapped_column(String(45))
    criado_em: Mapped[datetime] = mapped_column(default=agora)
#Extrato de pontos.... lá vamos nós.
class PontosMovimento(Base):
    __tablename__ = 'pontos_movimentos'

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'))
    pontos: Mapped[int]
    motivo: Mapped[str] = mapped_column(String(120))
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey('pedidos.id'))
    criado_em: Mapped[datetime] = mapped_column(default=agora)

class Cupom(Base):
    __tablename__ = 'cupons'

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)
    tipo: Mapped[str] = mapped_column(String(10)) #Percentual ou fixo
    valor: Mapped[int] #percentual ou centavos
    valido_ate: Mapped[date]
    ativo: Mapped[bool] = mapped_column(default=True)
    limite_usos: Mapped[int | None]
    usos: Mapped[int] = mapped_column(default=0)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuarios.id')) #cupom exclusivo de UM cliente (pra não sair repetindo)
    __table_args__ = (CheckConstraint('valor >0', name ='ck_cupom_valor'),)

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuarios.id'))
    acao: Mapped[str] = mapped_column(String(40))
    entidade: Mapped[str] = mapped_column(String(30))
    entidade_id: Mapped[int | None]
    detalhe: Mapped[str | None] = mapped_column(String(45))
    criado_em: Mapped[datetime] = mapped_column(default=agora)