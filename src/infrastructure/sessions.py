import logging

import jwt
from mcp.server.fastmcp import Context
from mcp.types import CallToolResult

from src.infrastructure.auth_required import get_bearer_token, require_auth
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.presentation.structured import session_result

logger = logging.getLogger(__name__)


@safe_tool
async def criar_sessao(ctx: Context) -> CallToolResult:
    """Cria uma sessao isolada para carrinho e listas."""
    request = ctx.request_context.request if ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err
    token_str = get_bearer_token(request)
    user_id = None
    if token_str:
        try:
            claims = jwt.decode(token_str, options={"verify_signature": False})
            user_id = claims.get("sub", "")
        except (jwt.InvalidTokenError, KeyError) as e:
            logger.warning("Failed to decode session JWT: %s", type(e).__name__)
            user_id = None

    if user_id:
        if not session_store.session_exists(user_id):
            session_store.create_session_with_id(user_id)
    else:
        user_id = session_store.create_session()

    return session_result(user_id)
