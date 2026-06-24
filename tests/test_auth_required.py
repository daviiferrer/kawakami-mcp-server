from src.infrastructure.auth_required import get_bearer_token, require_auth


class _FakeRequest:
    def __init__(self, auth_header: str = ""):
        self.headers = {"Authorization": auth_header} if auth_header else {}


class TestRequireAuth:
    def test_returns_error_when_no_request(self):
        result = require_auth(None)
        assert result is not None
        assert result.isError is True
        assert "Autenticacao necessaria" in result.content[0].text

    def test_returns_error_when_no_auth_header(self):
        result = require_auth(_FakeRequest(""))
        assert result is not None
        assert result.isError is True

    def test_returns_error_for_non_bearer_token(self):
        result = require_auth(_FakeRequest("Basic abc123"))
        assert result is not None
        assert result.isError is True

    def test_returns_none_for_valid_bearer(self):
        result = require_auth(_FakeRequest("Bearer some-valid-token"))
        assert result is None


class TestGetBearerToken:
    def test_returns_none_for_no_request(self):
        assert get_bearer_token(None) is None

    def test_returns_none_for_no_auth_header(self):
        assert get_bearer_token(_FakeRequest("")) is None

    def test_returns_none_for_non_bearer(self):
        assert get_bearer_token(_FakeRequest("Basic abc")) is None

    def test_returns_token_for_bearer(self):
        assert get_bearer_token(_FakeRequest("Bearer my-token")) == "my-token"
