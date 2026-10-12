import uuid

class GatewayTimeout(Exception):
    pass
class GatewayFalso: #Mock do pagamento.
    def cobrar (self, valor_centavos: int, metodo: str, simular: str, tentativa: int = 1) -> dict:
        if simular == 'TIMEOUT' or (simular == 'TIMEOUT_UMA_VEZ and tentativa == 1'):
            raise GatewayTimeout('O gateway não respondeu a tempo')
        aprovado = simular != 'RECUSADO'
        return {
            'transacaoId': str(uuid.uuid4()),
            'status': 'APROVADO' if aprovado else "RECUSADO",
            'valorCentavos': valor_centavos,
            'metodo': metodo,
            'motivo': None if aprovado else 'Pagamento recusado pelo emissor (simulação).',
        }
gateway = GatewayFalso()

