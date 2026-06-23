import jwt
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.types import CallToolResult

from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.presentation.structured import session_result


@safe_tool
async def criar_sessao() -> CallToolResult:
    """Cria uma sessao isolada para carrinho e listas."""
    token = get_access_token()
    user_id = None
    if token:
        try:
            claims = jwt.decode(token.token, options={"verify_signature": False})
            user_id = claims.get("sub", "")
        except Exception:
            user_id = None

    if user_id:
        if not session_store.session_exists(user_id):
            session_store.create_session_with_id(user_id)
    else:
        user_id = session_store.create_session()

    return session_result(user_id)
