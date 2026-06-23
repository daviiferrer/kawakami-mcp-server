from unittest.mock import patch

import pytest


def result_text(result) -> str:
    if isinstance(result, str):
        return result
    return result.content[0].text


class TestSearchProducts:
    @pytest.mark.asyncio
    async def test_buscar_produtos_returns_formatted_results(self, mock_vip_client):
        with patch("src.tools.busca.vip_client", mock_vip_client):
            from src.tools.busca import buscar_produtos

            result = await buscar_produtos("teste")
            text = result_text(result)
            assert "Mac. Nissin Lamen" in text
            assert "R$ 2,79" in text
            assert "OFERTA" in text

    @pytest.mark.asyncio
    async def test_buscar_produtos_empty_term(self, mock_vip_client):
        from src.tools.busca import buscar_produtos

        result = await buscar_produtos("")
        assert "termo de busca valido" in result.lower()

    @pytest.mark.asyncio
    async def test_buscar_por_ean_delegates_to_search(self, mock_vip_client):
        with patch("src.tools.busca.vip_client", mock_vip_client):
            from src.tools.busca import buscar_por_ean

            result = await buscar_por_ean("7891079000250")
            assert "Mac. Nissin" in result_text(result)


class TestCartTools:
    @pytest.mark.asyncio
    async def test_adicionar_ao_carrinho(self, mock_vip_client):
        with patch("src.tools.carrinho.vip_client", mock_vip_client):
            from src.infrastructure.session_store import session_store
            from src.tools.carrinho import adicionar_ao_carrinho, ver_carrinho

            session_id = session_store.create_session()
            result = await adicionar_ao_carrinho(session_id=session_id, termo="lamen")
            text = result_text(result)
            assert "+ Mac. Nissin" in text
            assert "Carrinho: 1 itens" in text

            cart = await ver_carrinho(session_id)
            assert "Mac. Nissin" in result_text(cart)

    @pytest.mark.asyncio
    async def test_limpar_carrinho(self, mock_vip_client):
        with patch("src.tools.carrinho.vip_client", mock_vip_client):
            from src.infrastructure.session_store import session_store
            from src.tools.carrinho import adicionar_ao_carrinho, limpar_carrinho, ver_carrinho

            session_id = session_store.create_session()
            await adicionar_ao_carrinho(session_id=session_id, termo="lamen")
            await limpar_carrinho(session_id)
            result = await ver_carrinho(session_id)
            assert "Carrinho vazio" in result_text(result)


class TestOfertas:
    @pytest.mark.asyncio
    async def test_ofertas_do_dia(self, mock_vip_client):
        with patch("src.tools.ofertas.vip_client", mock_vip_client):
            from src.tools.ofertas import ofertas_do_dia

            result = await ofertas_do_dia(limite=10)
            text = result_text(result)
            assert "MELHORES OFERTAS" in text
            assert "Mac. Nissin" in text


class TestFormatters:
    def test_format_price(self):
        from src.presentation.formatters import format_price

        assert format_price(2.79) == "R$ 2,79"
        assert format_price(0) == "R$ 0,00"
        assert format_price(1899.50) == "R$ 1899,50"

    def test_format_product_card(self):
        from src.domain.models import Produto
        from src.presentation.formatters import format_product_card

        p = Produto(
            produto_id=1,
            descricao="Teste",
            preco=10.0,
            unidade_sigla="UN",
            imagem="img.jpg",
            disponivel=True,
            quantidade_maxima=100,
            codigo_barras="123",
            link="teste",
        )
        result = format_product_card(p)
        assert "Teste" in result
        assert "R$ 10,00" in result
        assert "Disponivel: SIM" in result


class TestValidation:
    def test_sanitize_term(self):
        from src.infrastructure.validation import sanitize_term

        assert sanitize_term("leite ninho") == "leite ninho"
        assert sanitize_term("<script>alert(1)</script>") == "scriptalert1script"

    def test_sanitize_cep(self):
        from src.infrastructure.validation import sanitize_cep

        assert sanitize_cep("19700-000") == "19700000"
        assert sanitize_cep("19700000") == "19700000"
        assert sanitize_cep("abc") == "19700000"  # fallback

    def test_validate_quantidade(self):
        from src.infrastructure.validation import validate_quantidade

        assert validate_quantidade(5) == 5
        assert validate_quantidade(0) == 1
        assert validate_quantidade(2000) == 999
