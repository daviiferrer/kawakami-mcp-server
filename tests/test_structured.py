from src.domain.models import CarrinhoItem, Oferta, Produto
from src.presentation.structured import (
    _tag_kind,
    cart_result,
    product_to_ui,
    session_result,
)


class TestTagKind:
    def test_exclusive_tag(self):
        assert _tag_kind("exclusiva-do-app") == "exclusive"

    def test_app_tag(self):
        assert _tag_kind("app-only") == "exclusive"

    def test_club_tag(self):
        assert _tag_kind("clube-amigo") == "club"

    def test_amigo_tag(self):
        assert _tag_kind("amigo-fiel") == "club"

    def test_weekly_tag(self):
        assert _tag_kind("semanal") == "weekly"

    def test_empty_tag_returns_none(self):
        assert _tag_kind("") is None


class TestProductToUi:
    def test_without_offer(self):
        p = Produto(
            produto_id=1,
            descricao="Arroz",
            preco=10.0,
            unidade_sigla="KG",
            imagem="arroz.jpg",
            disponivel=True,
            quantidade_maxima=50,
        )
        ui = product_to_ui(p)
        assert ui["id"] == 1
        assert ui["name"] == "Arroz"
        assert ui["price"] == 10.0
        assert ui["offerPrice"] is None
        assert ui["originalPrice"] is None
        assert ui["tag"] is None
        assert ui["tagLabel"] is None

    def test_with_offer(self):
        o = Oferta(
            oferta_id=1,
            nome="Promo",
            tag="exclusiva-do-app",
            preco_oferta=7.0,
            preco_antigo=10.0,
        )
        p = Produto(
            produto_id=2,
            descricao="Feijao",
            preco=10.0,
            unidade_sigla="KG",
            imagem="feijao.jpg",
            disponivel=True,
            quantidade_maxima=30,
            em_oferta=True,
            oferta=o,
        )
        ui = product_to_ui(p)
        assert ui["offerPrice"] == 7.0
        assert ui["originalPrice"] == 10.0
        assert ui["tag"] == "exclusive"
        assert ui["tagLabel"] == "Promo"


class TestCartResult:
    def test_cart_result_structure(self):
        items = [
            CarrinhoItem(
                produto_id=1,
                nome="Arroz",
                preco_unit=10.0,
                quantidade=2,
                subtotal=20.0,
                un="KG",
                imagem="arroz.jpg",
                em_oferta=False,
            ),
        ]
        result = cart_result("Cart text", session_id="sess-1", cart=items)
        assert result.content[0].text == "Cart text"
        sc = result.structuredContent
        assert sc["sessionId"] == "sess-1"
        assert len(sc["cart"]) == 1
        assert sc["cart"][0]["id"] == 1
        assert sc["cart"][0]["quantity"] == 2
        assert sc["cart"][0]["subtotal"] == 20.0

    def test_empty_cart(self):
        result = cart_result("Empty", session_id="s", cart=[])
        assert result.structuredContent["cart"] == []


class TestSessionResult:
    def test_session_result(self):
        result = session_result("abc123")
        assert "abc123" in result.content[0].text
        assert result.structuredContent["sessionId"] == "abc123"
