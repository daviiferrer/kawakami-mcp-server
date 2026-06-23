from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.domain.exceptions import VipCommerceUnavailableError
from src.domain.models import Departamento, Produto
from src.infrastructure.vipcommerce_client import VipCommerceClient


def product_payload(product_id: int, *, offer: bool = False) -> dict:
    payload = {
        "produto_id": product_id,
        "descricao": f"Produto {product_id}",
        "preco": 10,
        "unidade_sigla": "UN",
        "imagem": "",
        "disponivel": True,
        "quantidade_maxima": 5,
        "em_oferta": offer,
    }
    if offer:
        payload["oferta"] = {
            "oferta_id": product_id,
            "nome": "Oferta",
            "tag": "oferta",
            "preco_oferta": 8,
            "preco_antigo": 10,
        }
    return payload


def json_response(payload: dict) -> httpx.Response:
    return httpx.Response(
        200,
        json=payload,
        request=httpx.Request("GET", "https://example.test"),
    )


@pytest.mark.asyncio
async def test_department_products_fetches_pages_until_limit():
    client = VipCommerceClient()
    request_mock = AsyncMock(
        side_effect=[
            json_response(
                {
                    "data": [product_payload(1), product_payload(2)],
                    "paginator": {"page": 1, "total_pages": 2, "total_items": 3},
                }
            ),
            json_response(
                {
                    "data": [product_payload(3)],
                    "paginator": {"page": 2, "total_pages": 2, "total_items": 3},
                }
            ),
        ]
    )

    try:
        with patch.object(client, "_request", request_mock):
            products, paginator = await client.get_products_by_department(
                7,
                limit=3,
                cep="17522363",
            )

        assert [product.produto_id for product in products] == [1, 2, 3]
        assert paginator["total_items"] == 3
        assert request_mock.await_args_list[0].kwargs["params"]["page"] == 1
        assert request_mock.await_args_list[1].kwargs["params"]["page"] == 2
        assert "/centro_distribuicao/1/" in request_mock.await_args_list[0].args[0]
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_best_offers_raises_when_every_department_fails():
    client = VipCommerceClient()
    departments = [
        Departamento(id=1, nome="A"),
        Departamento(id=2, nome="B"),
    ]

    try:
        with (
            patch.object(client, "get_departments", AsyncMock(return_value=departments)),
            patch.object(
                client,
                "get_products_by_department",
                AsyncMock(side_effect=VipCommerceUnavailableError("offline")),
            ),
        ):
            with pytest.raises(VipCommerceUnavailableError):
                await client.get_best_offers(10, cep="17522363")
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_product_lookup_propagates_cep_to_search():
    client = VipCommerceClient()
    product = Produto.from_api(product_payload(42))

    try:
        with patch.object(
            client,
            "search_products",
            AsyncMock(return_value=([product], {})),
        ) as search_mock:
            result = await client.get_product_by_id(42, cep="17522363")

        assert result is product
        search_mock.assert_awaited_once_with("42", page=1, cep="17522363")
    finally:
        await client.close()
