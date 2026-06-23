import functools
import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from src.domain.exceptions import (
    InvalidSessionError,
    ProdutoNotFoundError,
    TokenExpiredError,
    VipCommerceUnavailableError,
)

logger = logging.getLogger(__name__)

ERROR_MESSAGES = {
    VipCommerceUnavailableError: (
        "Supermercado Kawakami esta temporariamente indisponivel "
        "(atualizacao de precos da madrugada). Tente novamente em alguns minutos."
    ),
    TokenExpiredError: "Erro de autenticacao. O servidor tentara se reconectar automaticamente.",
    ProdutoNotFoundError: "Produto nao encontrado. Verifique o nome ou ID e tente novamente.",
    InvalidSessionError: "Sessao invalida ou expirada. Crie uma nova sessao antes de continuar.",
}


def safe_tool(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    """Converte exceções de domínio em respostas seguras para tools MCP."""
    sig = inspect.signature(func)

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except tuple(ERROR_MESSAGES.keys()) as e:
            msg = ERROR_MESSAGES.get(type(e), str(e))
            logger.warning("Tool %s failed: %s", func.__name__, msg)
            return msg
        except Exception as e:
            logger.error("Tool %s unexpected error: %s", func.__name__, str(e), exc_info=True)
            return f"Erro inesperado ao processar sua solicitacao. Detalhes: {type(e).__name__}"

    setattr(wrapper, "__signature__", sig)
    return wrapper
