class KawakamiError(Exception):
    """Base error for Kawakami MCP."""


class VipCommerceUnavailableError(KawakamiError):
    """VIP Commerce API is unreachable (503, timeout, connection refused)."""


class TokenExpiredError(KawakamiError):
    """Auth token expired and refresh failed."""


class ProdutoNotFoundError(KawakamiError):
    """Product not found by ID or search term."""


class InvalidSessionError(KawakamiError, ValueError):
    """Shopping session does not exist or has an invalid identifier."""
