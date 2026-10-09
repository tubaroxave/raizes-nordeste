# O CamelModel é pra fazer o Python usar preco_centavos e o JSON mostrar precoCentavos como pedido no roteiro.

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

class CardapioItemOut(CamelModel):
    produto_id: int
    nome: str
    categoria: str
    preco_centavos: int
    disponivel: bool
