from mcp.types import CallToolResult

from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.presentation.structured import session_result


@safe_tool
async def criar_sessao() -> CallToolResult:
    """Cria uma sessao isolada para carrinho e listas."""
    return session_result(session_store.create_session())
