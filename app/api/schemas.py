# O CamelModel é pra formatação dos resultados, como pedido no roteiro.
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel
from app.domain.enums import Perfil, TipoMovimento, CanalPedido, MetodoPagamento, SimulacaoGateway, StatusPedido, FinalidadeConsentimento, TipoCupom
from typing import Generic, TypeVar
from datetime import datetime, date

T = TypeVar('T')

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

class CardapioItemOut(CamelModel):
    produto_id: int
    nome: str
    categoria: str
    preco_centavos: int
    disponivel: bool

class RegistroIn(CamelModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    aceite_termos: bool

class LoginIn(CamelModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)

class UsuarioEquipeIn(CamelModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)
    perfil: Perfil

class UsuarioOut(CamelModel):
    id: int
    nome: str
    email: str
    perfil: str

class TokenOut(CamelModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UsuarioOut

class Pagina (CamelModel, Generic[T]):
    page: int
    limit: int
    total: int
    items: list[T]

class UnidadeOut(CamelModel):
    id: int
    nome: str
    cidade: str
    uf: str

class ProdutoIn(CamelModel):
    nome: str = Field(min_length=2, max_length=80)
    categoria: str = Field(min_length=2, max_lenght=30)
    preco_base_centavos: int = Field(ge=0)

class ProdutoAtualizaIn(ProdutoIn):
    ativo: bool

class ProdutoOut(CamelModel):
    id: int
    nome: str
    categoria: str
    preco_base_centavos: int
    ativo: bool

class CardapioItemIn(CamelModel):
    preco_centavos: int = Field(ge=0)
    disponível: bool = True

class MovimentoIn(CamelModel):
    unidade_id: int
    produto_id: int
    tipo: TipoMovimento
    quantidade: int = Field(gt=0, le=10000)
    motivo: str = Field(default='Ajuste manual', max_length=120)

class EstoqueOut(CamelModel):
    unidade_id: int
    produto_id: int
    nome: str
    quantidade: int


class ItemPedidoIn(CamelModel):
    produto_id: int
    quantidade: int = Field(gt=0, le=100)

class PedidoIn(CamelModel):
    unidade_id: int
    canal_pedido: CanalPedido 
    itens: list[ItemPedidoIn] = Field(min_length=1)
    cupom_codigo: str | None = Field(default=None, max_lenght=30)

class ItemPedidoOut(CamelModel):
    produto_id:int
    nome: str
    quantidade: int

class PedidoOut(CamelModel):
    id: int
    unidade_id: int
    cliente_id: int | None
    canal_pedido: str
    status: str
    subtotal_centavos: int
    desconto_centavos: int
    total_centavos: int
    cupom_codigo: str | None
    criado_em: datetime
    itens: list[ItemPedidoOut]

class StatusIn(CamelModel):
    status: StatusPedido

class PagamentoIn(CamelModel):
    pedido_id: int
    metodo: MetodoPagamento
    simular: SimulacaoGateway = SimulacaoGateway.APROVADO

class PagamentoOut(CamelModel):
    id: int
    pedido_id: int
    status: str
    metodo: str
    valor_centavos: int
    transacao_id: str | None
    tentativas: int
    pedido_status: str

class ConsentimentoIn(CamelModel):
    finalidade: FinalidadeConsentimento
    aceito: bool
    versao_termo: str = Field(min_length=1, max_length=10)

class ConsentimentoOut(CamelModel):
    finalidade: str
    aceito: bool
    versao_termo: str
    criado_em: datetime

class SaldoOut(CamelModel):
    pontos: int
    consentimento_fidelidade: bool

class ResgateIn(CamelModel):
    pontos: int = Field(ge=100, le=100000)

class CupomIn(CamelModel):
    codigo: str = Field(min_length=3, max_length=30)
    tipo: TipoCupom
    valor: int = Field(gt=0)
    valido_ate: date
    limite_usos: int | None = Field(default=None, ge=1)

class CupomOut(CamelModel):
    codigo: str
    tipo: str
    valor: int
    valido_ate: date
    usos: int
    limite_usos: int | None