from unittest.mock import MagicMock, patch

import jwt
import pytest

from src.infrastructure.auth0_verifier import Auth0TokenVerifier


@pytest.mark.asyncio
async def test_verify_valid_token_returns_access_token():
    verifier = Auth0TokenVerifier.__new__(Auth0TokenVerifier)
    verifier._jwks = MagicMock()
    verifier._audience = "https://test-mcp"
    verifier._issuer = "https://test.auth0.com/"

    claims = {
        "sub": "auth0|123",
        "iss": "https://test.auth0.com/",
        "aud": "https://test-mcp",
        "exp": 9999999999,
        "scope": "cart:read cart:write",
        "azp": "test-client-id",
    }

    mock_key = type("Key", (), {"key": "secret"})()
    verifier._jwks.get_signing_key_from_jwt.return_value = mock_key

    with patch("jwt.decode", return_value=claims):
        result = await verifier.verify_token("fake-token")

    assert result is not None
    assert result.token == "fake-token"
    assert result.scopes == ["cart:read", "cart:write"]
    assert result.client_id == "test-client-id"


@pytest.mark.asyncio
async def test_verify_expired_token_returns_none():
    verifier = Auth0TokenVerifier.__new__(Auth0TokenVerifier)
    verifier._jwks = MagicMock()
    verifier._audience = "https://test-mcp"
    verifier._issuer = "https://test.auth0.com/"

    mock_key = type("Key", (), {"key": "secret"})()
    verifier._jwks.get_signing_key_from_jwt.return_value = mock_key

    with patch("jwt.decode", side_effect=jwt.ExpiredSignatureError):
        result = await verifier.verify_token("expired-token")

    assert result is None


@pytest.mark.asyncio
async def test_verify_invalid_issuer_returns_none():
    verifier = Auth0TokenVerifier.__new__(Auth0TokenVerifier)
    verifier._jwks = MagicMock()
    verifier._audience = "https://test-mcp"
    verifier._issuer = "https://test.auth0.com/"

    mock_key = type("Key", (), {"key": "secret"})()
    verifier._jwks.get_signing_key_from_jwt.return_value = mock_key

    with patch("jwt.decode", side_effect=jwt.InvalidIssuerError):
        result = await verifier.verify_token("bad-issuer-token")

    assert result is None
