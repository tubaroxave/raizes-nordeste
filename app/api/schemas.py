# O CamelModel é pra fazer o Python usar preco_centavos e o JSON mostrar precoCentavos como pedido no roteiro.
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel
from app.domain.enums import Perfil
from typing import Generic, TypeVar

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