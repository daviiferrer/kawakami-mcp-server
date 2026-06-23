import jwt
from contextvars import ContextVar
from mcp.types import CallToolResult, TextContent
from mcp.server.auth.middleware.auth_context import get_access_token
from src.config import settings


def require_auth() -> CallToolResult | None:
    token = get_access_token()
    if not token or not token.token:
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
