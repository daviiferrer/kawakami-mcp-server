import uuid
from typing import Optional

from mcp.server.fastmcp import Context

_sid_fallback: str | None = None


def get_sid(ctx: Optional[Context] = None) -> str:
    """Retorna session ID do MCP se disponivel, ou fallback unico."""
    global _sid_fallback
    if ctx is not None:
        sid = getattr(ctx, "session_id", None) or getattr(getattr(ctx, "session", None), "id", None)
        if sid:
            return str(sid)
    if _sid_fallback is None:
        _sid_fallback = uuid.uuid4().hex[:12]
    return _sid_fallback
