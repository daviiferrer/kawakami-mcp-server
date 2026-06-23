import logging

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier

from src.config import settings

logger = logging.getLogger(__name__)


class Auth0TokenVerifier(TokenVerifier):
    """Validates Auth0 JWT tokens against JWKS."""

    def __init__(self) -> None:
        if not settings.auth0_domain:
            raise RuntimeError("KWK_AUTH0_DOMAIN is required for OAuth")
        self._jwks = PyJWKClient(settings.auth0_jwks_url())
        self._audience = settings.auth0_audience
        self._issuer = settings.auth0_issuer()

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iss", "sub", "aud"]},
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Auth0 token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid Auth0 token: %s", e)
            return None

        scopes_str = claims.get("scope", "")
        scopes = scopes_str.split() if scopes_str else []

        return AccessToken(
            token=token,
            client_id=claims.get("azp", ""),
            scopes=scopes,
            expires_at=claims.get("exp"),
            resource=claims.get("aud", ""),
        )
