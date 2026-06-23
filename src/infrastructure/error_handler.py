import functools
import logging

from src.domain.exceptions import VipCommerceUnavailableError, TokenExpiredError, ProdutoNotFoundError

logger = logging.getLogger(__name__)

ERROR_MESSAGES = {
    VipCommerceUnavailableError: (
        "Supermercado Kawakami esta temporariamente indisponivel "
        "(atualizacao de precos da madrugada). Tente novamente em alguns minutos."
    ),
    TokenExpiredError: "Erro de autenticacao. O servidor tentara se reconectar automaticamente.",
    ProdutoNotFoundError: "Produto nao encontrado. Verifique o nome ou ID e tente novamente.",
}


def safe_tool(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except tuple(ERROR_MESSAGES.keys()) as e:
            msg = ERROR_MESSAGES.get(type(e), str(e))
            logger.warning("Tool %s failed: %s", func.__name__, msg)
            return msg
        except Exception as e:
            logger.error("Tool %s unexpected error: %s", func.__name__, str(e), exc_info=True)
            return f"Erro inesperado ao processar sua solicitacao. Detalhes: {type(e).__name__}"

    return wrapper
