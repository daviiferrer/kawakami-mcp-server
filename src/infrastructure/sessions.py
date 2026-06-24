import logging

import jwt
from jwt import PyJWKClient
from mcp.server.fastmcp import Context
from mcp.types import CallToolResult

from src.config import settings
from src.infrastructure.auth_required import get_bearer_token, require_auth
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.presentation.structured import session_result

logger = logging.getLogger(__name__)

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient | None:
    global _jwks_client
    if _jwks_client is None and settings.auth0_domain:
        _jwks_client = PyJWKClient(
            f"https://{settings.auth0_domain}/.well-known/jwks.json"
        )
    return _jwks_client


def _extract_verified_sub(token_str: str) -> str | None:
    """Extract the 'sub' claim from a JWT after verifying its signature."""
    if not token_str:
        return None

    jwks = _get_jwks_client()
    if not jwks:
        logger.warning("Auth0 not configured; cannot verify JWT signature")
        return None

    try:
        signing_key = jwks.get_signing_key_from_jwt(token_str)
        audience = settings.auth0_audience or "https://kawakami.axischat.com.br"
        claims = jwt.decode(
            token_str,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=f"https://{settings.auth0_domain}/",
            options={"require": ["exp", "iss", "sub", "aud"]},
        )
        return claims.get("sub") or None
    except jwt.ExpiredSignatureError:
        logger.warning("JWT expired during session creation")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT during session creation: %s", type(e).__name__)
        return None


@safe_tool
async def criar_sessao(ctx: Context) -> CallToolResult:
    """Cria uma sessao isolada para carrinho e listas."""
    request = ctx.request_context.request if ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err

    token_str = get_bearer_token(request)
    user_id = _extract_verified_sub(token_str) if token_str else None

    if user_id:
        if not session_store.session_exists(user_id):
            session_store.create_session_with_id(user_id)
    else:
        user_id = session_store.create_session()

    return session_result(user_id)
