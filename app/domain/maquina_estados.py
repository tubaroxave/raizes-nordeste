from app.domain.errors import AppError

TRANSICOES = {
    'AGUARDANDO_PAGAMENTO': {'PAGO', 'PAGAMENTO_RECUSADO', 'CANCELADO'},
    'PAGAMENTO_RECUSADO': {'PAGO', 'PAGAMENTO_RECUSADO', 'CANCELADO'},
    'PAGO': {'EM_PREPARO', 'CANCELADO'},
    'EM_PREPARO': {'PRONTO', 'CANCELADO'},
    'PRONTO': {'ENTREGUE'},
    'ENTREGUE': set(),
    'CANCELADO': set(),
}

#Permissões
QUEM_PODE_MOVER_PARA = {
    'EM_PREPARO': {'COZINHA', 'GERENTE', 'ADMIN'},
    'PRONTO': {'COZINHA', 'GERENTE', 'ADMIN'},
    'ENTREGUE': {'ATENDENTE', 'GERENTE', 'ADMIN'},

}

def validar_transicao(atual: str, novo: str) -> None:
    if novo not in TRANSICOES[atual]:
        raise AppError(409, 'TRANSICAO_INVALIDA', f'Não é possível ir de {atual} para {novo}.', [{'field': 'status', 'issue': f'{atual} -> {novo} não é permitido.'}])

def validar_mudanca_manual(atual: str, novo: str, perfil: str) -> None:
    if novo not in QUEM_PODE_MOVER_PARA:
        raise AppError(409, 'STATUS_DEFINIDO_PELO_SISTEMA', f'O status {novo} não pode ser definido por este endpoint.')
    if perfil not in QUEM_PODE_MOVER_PARA[novo]:
        raise AppError(403, 'SEM_PERMISSAO', f'O perfil {perfil} não pode mover pedidos para {novo}.')
    validar_transicao(atual,novo)                  