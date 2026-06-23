from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.infrastructure.auth import token_manager
from src.infrastructure.vipcommerce_client import VipCommerceClient


@pytest.mark.asyncio
async def test_request_uses_refreshed_token_on_retry():
    original_token = token_manager._token
    original_session_id = token_manager._sessao_id
    token_manager._token = "expired-token"
    token_manager._sessao_id = "session-a"
    client = VipCommerceClient()
    responses = [
        httpx.Response(401, request=httpx.Request("GET", "https://example.test")),
        httpx.Response(
            200, json={"ok": True}, request=httpx.Request("GET", "https://example.test")
        ),
    ]
    get_mock = AsyncMock(side_effect=responses)

    async def refresh_token() -> bool:
        token_manager._token = "fresh-token"
        token_manager._sessao_id = "session-b"
        return True

    try:
        with (
            patch.object(client._client, "get", get_mock),
            patch.object(token_manager, "refresh", refresh_token),
        ):
            await client._request("https://example.test", retries=2)

        first_headers = get_mock.await_args_list[0].kwargs["headers"]
        second_headers = get_mock.await_args_list[1].kwargs["headers"]
        assert first_headers["authorization"] == "Bearer expired-token"
        assert second_headers["authorization"] == "Bearer fresh-token"
        assert second_headers["sessao-id"] == "session-b"
    finally:
        token_manager._token = original_token
        token_manager._sessao_id = original_session_id
        await client.close()
