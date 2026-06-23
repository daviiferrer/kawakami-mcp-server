from mcp.types import CallToolResult, TextContent
from src.config import settings


def require_auth(request=None) -> CallToolResult | None:
    """Check Bearer token from HTTP request. Returns None if OK, error result if auth needed."""
    token = None
    if request:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
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
                    f'error_description="Login required to access cart and links"'
                ]
            },
            isError=True,
        )
    return None


def get_bearer_token(request=None) -> str | None:
    """Extract Bearer token from request."""
    if not request:
        return None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None
