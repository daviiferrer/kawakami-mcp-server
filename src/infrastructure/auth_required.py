import jwt
from contextvars import ContextVar

from mcp.types import CallToolResult, TextContent

from src.config import settings

_auth_token: ContextVar[str | None] = ContextVar("auth_token", default=None)


def set_auth_token(token: str | None) -> None:
    _auth_token.set(token)


def get_auth_token() -> str | None:
    return _auth_token.get(None)


def require_auth() -> CallToolResult | None:
    token = get_auth_token()
    if not token:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Autenticacao necessaria. Vincule sua conta para usar carrinho e listas.",
            )],
            _meta={
                "mcp/www_authenticate": [
                    f'Bearer resource_metadata="{settings.auth0_audience}'
                    f'/.well-known/oauth-protected-resource", '
                    f'error="insufficient_scope", '
                    f'error_description="Login required to access cart and lists"'
                ]
            },
            isError=True,
        )
    return None
