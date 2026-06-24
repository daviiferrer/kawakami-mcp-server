import pytest

from src.domain.exceptions import (
    InvalidSessionError,
    ProdutoNotFoundError,
    TokenExpiredError,
    VipCommerceUnavailableError,
)
from src.infrastructure.error_handler import safe_tool


class TestSafeTool:
    @pytest.mark.asyncio
    async def test_returns_result_on_success(self):
        @safe_tool
        async def ok_tool():
            return "all good"

        result = await ok_tool()
        assert result == "all good"

    @pytest.mark.asyncio
    async def test_catches_vip_commerce_unavailable(self):
        @safe_tool
        async def failing_tool():
            raise VipCommerceUnavailableError("down")

        result = await failing_tool()
        assert "temporariamente indisponivel" in result

    @pytest.mark.asyncio
    async def test_catches_token_expired(self):
        @safe_tool
        async def failing_tool():
            raise TokenExpiredError("expired")

        result = await failing_tool()
        assert "autenticacao" in result.lower()

    @pytest.mark.asyncio
    async def test_catches_produto_not_found(self):
        @safe_tool
        async def failing_tool():
            raise ProdutoNotFoundError("missing")

        result = await failing_tool()
        assert "nao encontrado" in result.lower()

    @pytest.mark.asyncio
    async def test_catches_invalid_session(self):
        @safe_tool
        async def failing_tool():
            raise InvalidSessionError("bad session")

        result = await failing_tool()
        assert "sessao invalida" in result.lower()

    @pytest.mark.asyncio
    async def test_catches_unexpected_exception(self):
        @safe_tool
        async def failing_tool():
            raise RuntimeError("boom")

        result = await failing_tool()
        assert "Erro inesperado" in result
        assert "RuntimeError" in result

    @pytest.mark.asyncio
    async def test_preserves_function_signature(self):
        import inspect

        @safe_tool
        async def my_tool(a: int, b: str = "x") -> str:
            return f"{a}{b}"

        sig = inspect.signature(my_tool)
        params = list(sig.parameters.keys())
        assert "a" in params
        assert "b" in params

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        @safe_tool
        async def add_tool(x: int, y: int) -> int:
            return x + y

        result = await add_tool(3, y=4)
        assert result == 7
