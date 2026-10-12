#Pensa num script que está me dando dúvida.

import logging
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain.errors import AppError

logger = logging.getLogger('raizes')

def resposta(request: Request, status: int, error: str, message: str, details: list | None = None) -> JSONResponse:
    corpo = {
        'error': error,
        'message': message,
        'details': details or [],
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'path': request.url.path,
        'requestId': getattr(request.state, 'request_id', str(uuid.uuid4()))
}
    return JSONResponse(status_code=status, content=corpo)

def registrar_handlers(app: FastAPI) -> None:
    @app.middleware('http')
    async def adicionar_request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        resposta = await call_next(request)
        resposta.headers['X-Request-Id'] = request.state.request_id
        return resposta
    @app.exception_handler(AppError)
    async def tratar_app_error(request: Request, exc: AppError):
        return resposta (request, exc.status, exc.error, exc.message, exc.details)
    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(request: Request, exc: RequestValidationError):
        detalhes = [{'field': '.'.join(str(p) for p in e['loc'][1:]), 'issue': e['msg']} for e in exc.errors ()]
        return resposta(request, 422, 'VALIDACAO_FALHOU', 'Há campos inválidos na requisição.', detalhes)

    @app.exception_handler(StarletteHTTPException)
    async def tratar_http(request: Request, exc: StarletteHTTPException):
        #Codigo de erros.
        codigos = {404: 'ROTA_NAO_ENCONTRADA', 405: 'METODO_NAO_PERMITIDO'}
        return resposta(request, exc.status_code, codigos.get(exc.status_code, 'ERRO_HTTP'), str(exc.detail))

    @app.exception_handler(Exception)
    async def tratar_inesperado(request: Request, exc: Exception):
        logger.error('Erro inesperado em %s', request.url.path, exc_info=exc)
        #O detalhe vai ficar no log e não vai pro cliente. Mas vou testar isso direito depois, mas em TEORIA funciona.
        return resposta(request, 500, 'ERRO_INTERNO', "Erro interno. Informe o requestId ao suporte.")
    