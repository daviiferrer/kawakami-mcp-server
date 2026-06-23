from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_vip_client():
    from src.domain.models import Oferta, Produto

    produto = Produto(
        produto_id=285,
        descricao="Mac. Nissin Lamen 85g Bacon",
        preco=3.18,
        unidade_sigla="UN",
        imagem="img.jpg",
        disponivel=True,
        quantidade_maxima=172,
        codigo_barras="7891079000250",
        sku="64-0011D",
        em_oferta=True,
        oferta=Oferta(
            oferta_id=88084,
            nome="Exclusiva do App e Site",
            tag="exclusiva-do-app-e-site",
            preco_oferta=2.79,
            preco_antigo=3.18,
        ),
    )

    mock = AsyncMock()
    mock.search_products.return_value = ([produto], {"total_items": 1, "page": 1, "total_pages": 1})
    mock.get_departments.return_value = []
    mock.get_product_by_id.return_value = produto
    mock.get_best_offers.return_value = [produto]
    return mock
