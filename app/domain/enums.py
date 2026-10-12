from enum import Enum

class Perfil(str, Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE = "GERENTE"
    ADMIN = "ADMIN"

class TipoMovimento(str, Enum):
    ENTRADA = 'ENTRADA'
    SAIDA = 'SAIDA'



class CanalPedido(str, Enum):
    APP = 'APP'
    TOTEM = 'TOTEM'
    BALCAO = 'BALCAO'
    PICKUP = 'PICKUP'
    WEB = 'WEB'


class StatusPedido(str, Enum):
    AGUARDANDO_PAGAMENTO = 'AGUARDANDO_PAGAMENTO'
    PAGO = 'PAGO'
    PAGAMENTO_RECUSADO = 'PAGAMENTO_RECUSADO'
    EM_PREPARO = 'EM_PREPARO'
    PRONTO = 'PRONTO'
    ENTREGUE = 'ENTREGUE'
    CANCELADO = 'CANCELADO'

class MetodoPagamento(str, Enum):
    PIX = 'PIX'
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = 'CARTAO_DEBITO'

class SimulacaoGateway(str, Enum):
    APROVADO = 'APROVADO'
    RECUSADO = 'RECUSADO'
    TIMEOUT = "TIMEOUT"
    TIMEOUT_UMA_VEZ = "TIMEOUT_UMA_VEZ" #Falha na primeira e aí funciona na segunda


class TipoCupom(str, Enum):
    PERCENTUAL = 'PERCENTUAL'
    FIXO = 'FIXO'

class FinalidadeConsentimento(str, Enum):
    FIDELIDADE = "FIDELIDADE"