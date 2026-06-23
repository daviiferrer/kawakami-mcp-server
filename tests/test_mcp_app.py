from unittest.mock import patch

import pytest
from mcp.types import CallToolResult

from src.domain.models import Oferta, Produto


@pytest.fixture
def offer_product() -> Produto:
    return Produto(
        produto_id=285,
        descricao="Mac. Nissin Lamen 85g Bacon",
        preco=3.18,
        unidade_sigla="UN",
        imagem="produto.jpg",
        disponivel=True,
        quantidade_maxima=172,
        em_oferta=True,
        oferta=Oferta(
            oferta_id=1,
            nome="Exclusiva",
            tag="exclusiva-do-app-e-site",
            preco_oferta=2.79,
            preco_antigo=3.18,
        ),
    )


@pytest.mark.asyncio
async def test_offers_returns_widget_structured_content(mock_vip_client, offer_product):
    mock_vip_client.get_best_offers.return_value = [offer_product]
    with patch("src.tools.ofertas.vip_client", mock_vip_client):
        from src.tools.ofertas import ofertas_do_dia

        result = await ofertas_do_dia(limite=10)

    assert isinstance(result, CallToolResult)
    assert result.structuredContent == {
        "sections": [
            {
                "key": "offers",
                "title": "Ofertas do Dia",
                "products": [
                    {
                        "id": 285,
                        "name": "Mac. Nissin Lamen 85g Bacon",
                        "price": 3.18,
                        "offerPrice": 2.79,
                        "originalPrice": 3.18,
                        "unit": "UN",
                        "image": "produto.jpg",
                        "stock": 172,
                        "tag": "exclusive",
                        "tagLabel": "Exclusiva",
                    }
                ],
            }
        ]
    }


@pytest.mark.asyncio
async def test_server_registers_widget_resource_and_tool_metadata():
    from src.presentation.widget import (
        WIDGET_MIME_TYPE,
        WIDGET_RESOURCE_META,
        WIDGET_URI,
    )
    from src.server import create_mcp

    mcp = create_mcp()
    tools = await mcp.list_tools()
    resources = await mcp.list_resources()

    offers_tool = next(tool for tool in tools if tool.name == "ofertas_do_dia")
    widget_resource = next(resource for resource in resources if str(resource.uri) == WIDGET_URI)

    assert WIDGET_URI == "ui://kawakami/catalog-v2.html"
    assert WIDGET_RESOURCE_META["ui"]["prefersBorder"] is False
    assert offers_tool.meta["ui"]["resourceUri"] == WIDGET_URI
    assert widget_resource.mimeType == WIDGET_MIME_TYPE


def test_widget_loader_inlines_built_assets(tmp_path):
    from src.presentation.widget import load_widget_html

    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.css").write_text("body{color:red}", encoding="utf-8")
    (tmp_path / "assets" / "app.js").write_text("window.__APP__=true", encoding="utf-8")
    (tmp_path / "index.html").write_text(
        (
            '<html><head><link rel="stylesheet" href="/assets/app.css"></head>'
            '<body><div id="root"></div>'
            '<script type="module" src="/assets/app.js"></script></body></html>'
        ),
        encoding="utf-8",
    )

    html = load_widget_html(tmp_path)

    assert "<style>body{color:red}</style>" in html
    assert '<script type="module">window.__APP__=true</script>' in html
    assert 'href="/assets/app.css"' not in html
    assert 'src="/assets/app.js"' not in html
