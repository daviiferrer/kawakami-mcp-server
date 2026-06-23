import jwt
from mcp.types import CallToolResult

from src.infrastructure.auth_required import get_auth_token, require_auth
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.presentation.structured import session_result


@safe_tool
async def criar_sessao() -> CallToolResult:
    """Cria uma sessao isolada para carrinho e listas."""
    auth_err = require_auth()
    if auth_err is not None:
        return auth_err
    token = get_auth_token()
    user_id = None
    if token:
        try:
            claims = jwt.decode(token, options={"verify_signature": False})
            user_id = claims.get("sub", "")
        except Exception:
            user_id = None

    if user_id:
        if not session_store.session_exists(user_id):
            session_store.create_session_with_id(user_id)
    else:
        user_id = session_store.create_session()

    return session_result(user_id)
