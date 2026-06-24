import pytest

from src.domain.exceptions import InvalidSessionError
from src.domain.models import CarrinhoItem, ListaCompras
from src.infrastructure.session_store import SessionStore


@pytest.fixture
def store(tmp_path):
    return SessionStore(tmp_path / "test.db")


def _make_item(produto_id: int = 1, nome: str = "Arroz") -> CarrinhoItem:
    return CarrinhoItem(
        produto_id=produto_id,
        nome=nome,
        preco_unit=10.0,
        quantidade=2,
        subtotal=20.0,
        un="KG",
        imagem="img.jpg",
    )


class TestSessionCreation:
    def test_create_session_with_id(self, store):
        sid = store.create_session_with_id("custom-id-123")
        assert sid == "custom-id-123"
        assert store.session_exists("custom-id-123")

    def test_create_session_with_id_is_idempotent(self, store):
        store.create_session_with_id("dup-id")
        store.create_session_with_id("dup-id")
        assert store.session_exists("dup-id")


class TestCartOperations:
    def test_add_to_cart(self, store):
        sid = store.create_session()
        item = _make_item()
        cart = store.add_to_cart(sid, item)
        assert len(cart) == 1
        assert cart[0].nome == "Arroz"
        assert cart[0].quantidade == 2

    def test_add_replaces_same_produto_id(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Arroz v1"))
        cart = store.add_to_cart(sid, _make_item(1, "Arroz v2"))
        assert len(cart) == 1
        assert cart[0].nome == "Arroz v2"

    def test_add_multiple_different_items(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Arroz"))
        cart = store.add_to_cart(sid, _make_item(2, "Feijao"))
        assert len(cart) == 2

    def test_add_to_invalid_session_raises(self, store):
        with pytest.raises(InvalidSessionError):
            store.add_to_cart("nonexistent", _make_item())

    def test_get_cart_empty(self, store):
        sid = store.create_session()
        cart = store.get_cart(sid)
        assert cart == []

    def test_get_cart_invalid_session(self, store):
        with pytest.raises(InvalidSessionError):
            store.get_cart("nonexistent")

    def test_remove_from_cart_exact_match(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Arroz Tio Joao"))
        store.add_to_cart(sid, _make_item(2, "Feijao Carioca"))
        removed = store.remove_from_cart(sid, "Arroz")
        assert removed is not None
        assert removed.nome == "Arroz Tio Joao"
        cart = store.get_cart(sid)
        assert len(cart) == 1

    def test_remove_returns_none_for_no_match(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Arroz"))
        removed = store.remove_from_cart(sid, "Leite")
        assert removed is None

    def test_remove_returns_none_for_ambiguous_match(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Leite Integral"))
        store.add_to_cart(sid, _make_item(2, "Leite Desnatado"))
        removed = store.remove_from_cart(sid, "Leite")
        assert removed is None

    def test_clear_cart(self, store):
        sid = store.create_session()
        store.add_to_cart(sid, _make_item(1, "Arroz"))
        store.add_to_cart(sid, _make_item(2, "Feijao"))
        store.clear_cart(sid)
        assert store.get_cart(sid) == []

    def test_clear_cart_invalid_session(self, store):
        with pytest.raises(InvalidSessionError):
            store.clear_cart("nonexistent")

    def test_cart_preserves_offer_fields(self, store):
        sid = store.create_session()
        item = CarrinhoItem(
            produto_id=1,
            nome="Promo Item",
            preco_unit=5.0,
            quantidade=1,
            subtotal=5.0,
            un="UN",
            imagem="promo.jpg",
            em_oferta=True,
            tag="club-offer",
        )
        cart = store.add_to_cart(sid, item)
        assert cart[0].em_oferta is True
        assert cart[0].tag == "club-offer"


class TestListOperations:
    def _make_lista(self) -> ListaCompras:
        return ListaCompras(
            nome="Semanal",
            itens=[_make_item(1, "Arroz"), _make_item(2, "Feijao")],
            total=40.0,
            criado_em="01/01/2025 10:00",
            cep="19700000",
        )

    def test_save_and_get_list(self, store):
        sid = store.create_session()
        lista = self._make_lista()
        store.save_list(sid, "Semanal", lista)
        retrieved = store.get_list(sid, "Semanal")
        assert retrieved is not None
        assert retrieved.nome == "Semanal"
        assert len(retrieved.itens) == 2
        assert retrieved.total == 40.0
        assert retrieved.cep == "19700000"

    def test_get_nonexistent_list(self, store):
        sid = store.create_session()
        assert store.get_list(sid, "Nonexistent") is None

    def test_get_list_invalid_session(self, store):
        with pytest.raises(InvalidSessionError):
            store.get_list("bad-session", "X")

    def test_save_list_replaces_existing(self, store):
        sid = store.create_session()
        store.save_list(sid, "Semanal", self._make_lista())
        new_lista = ListaCompras(
            nome="Semanal",
            itens=[_make_item(3, "Leite")],
            total=10.0,
            criado_em="02/01/2025",
            cep="19700000",
        )
        store.save_list(sid, "Semanal", new_lista)
        retrieved = store.get_list(sid, "Semanal")
        assert len(retrieved.itens) == 1
        assert retrieved.itens[0].nome == "Leite"

    def test_get_all_lists(self, store):
        sid = store.create_session()
        store.save_list(sid, "Lista1", self._make_lista())
        lista2 = ListaCompras(nome="Lista2", itens=[], total=0.0, criado_em="", cep="")
        store.save_list(sid, "Lista2", lista2)
        all_lists = store.get_all_lists(sid)
        assert len(all_lists) == 2
        assert "Lista1" in all_lists
        assert "Lista2" in all_lists

    def test_get_all_lists_empty(self, store):
        sid = store.create_session()
        assert store.get_all_lists(sid) == {}

    def test_delete_list(self, store):
        sid = store.create_session()
        store.save_list(sid, "ToDelete", self._make_lista())
        assert store.delete_list(sid, "ToDelete") is True
        assert store.get_list(sid, "ToDelete") is None

    def test_delete_nonexistent_list(self, store):
        sid = store.create_session()
        assert store.delete_list(sid, "Ghost") is False

    def test_save_list_invalid_session(self, store):
        with pytest.raises(InvalidSessionError):
            store.save_list("bad", "X", self._make_lista())

    def test_delete_list_invalid_session(self, store):
        with pytest.raises(InvalidSessionError):
            store.delete_list("bad", "X")
