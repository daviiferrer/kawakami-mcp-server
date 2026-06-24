import logging

import jwt
from jwt import PyJWKClient
from mcp.types import CallToolResult, TextContent

from src.config import settings

logger = logging.getLogger(__name__)

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient | None:
    global _jwks_client
    if _jwks_client is None and settings.auth0_domain:
        _jwks_client = PyJWKClient(
            f"https://{settings.auth0_domain}/.well-known/jwks.json"
        )
    return _jwks_client


def _auth_error(text: str) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        _meta={
            "mcp/www_authenticate": [
                f'Bearer resource_metadata="{settings.auth0_audience}'
                f'/.well-known/oauth-protected-resource", '
                f'error="insufficient_scope", '
                f'error_description="Login required to access cart and links"'
            ]
        },
        isError=True,
    )


def require_auth(request=None) -> CallToolResult | None:
    """Validate Bearer token from HTTP request. Returns None if OK, error result otherwise."""
    token = None
    if request:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return _auth_error(
            "Autenticacao necessaria. Vincule sua conta para usar carrinho e listas."
        )

    jwks = _get_jwks_client()
    if not jwks:
        # Auth0 not configured — accept token presence only (stdio/dev mode)
        return None

    try:
        signing_key = jwks.get_signing_key_from_jwt(token)
        audience = settings.auth0_audience or "https://kawakami.axischat.com.br"
        jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=f"https://{settings.auth0_domain}/",
            options={"require": ["exp", "iss", "sub", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        return _auth_error("Token expirado. Faca login novamente.")
    except jwt.InvalidTokenError:
        return _auth_error("Token invalido. Faca login novamente.")

    return None


def get_bearer_token(request=None) -> str | None:
    """Extract Bearer token from request."""
    if not request:
        return None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None
