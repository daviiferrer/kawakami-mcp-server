from src.domain.models import CarrinhoItem, Departamento, ListaCompras, Oferta, Produto


class TestOferta:
    def test_desconto_pct_normal(self):
        o = Oferta(oferta_id=1, nome="X", tag="x", preco_oferta=8.0, preco_antigo=10.0)
        assert o.desconto_pct == 20

    def test_desconto_pct_zero_when_antigo_is_zero(self):
        o = Oferta(oferta_id=1, nome="X", tag="x", preco_oferta=5.0, preco_antigo=0.0)
        assert o.desconto_pct == 0.0

    def test_desconto_pct_high_discount(self):
        o = Oferta(oferta_id=1, nome="X", tag="x", preco_oferta=1.0, preco_antigo=10.0)
        assert o.desconto_pct == 90

    def test_default_quantidade_values(self):
        o = Oferta(oferta_id=1, nome="X", tag="x", preco_oferta=5.0, preco_antigo=10.0)
        assert o.quantidade_minima == 1
        assert o.quantidade_maxima == 6


class TestProduto:
    def test_preco_efetivo_without_offer(self):
        p = Produto(
            produto_id=1,
            descricao="Test",
            preco=10.0,
            unidade_sigla="UN",
            imagem="",
            disponivel=True,
            quantidade_maxima=5,
        )
        assert p.preco_efetivo == 10.0

    def test_preco_efetivo_with_offer(self):
        o = Oferta(oferta_id=1, nome="X", tag="x", preco_oferta=7.0, preco_antigo=10.0)
        p = Produto(
            produto_id=1,
            descricao="Test",
            preco=10.0,
            unidade_sigla="UN",
            imagem="",
            disponivel=True,
            quantidade_maxima=5,
            em_oferta=True,
            oferta=o,
        )
        assert p.preco_efetivo == 7.0

    def test_preco_efetivo_em_oferta_but_no_oferta_object(self):
        p = Produto(
            produto_id=1,
            descricao="Test",
            preco=10.0,
            unidade_sigla="UN",
            imagem="",
            disponivel=True,
            quantidade_maxima=5,
            em_oferta=True,
            oferta=None,
        )
        assert p.preco_efetivo == 10.0

    def test_from_api_minimal(self):
        data = {
            "produto_id": 42,
            "descricao": "Arroz 5kg",
            "preco": 25.90,
            "unidade_sigla": "UN",
            "imagem": "arroz.jpg",
            "disponivel": True,
            "quantidade_maxima": 50,
        }
        p = Produto.from_api(data)
        assert p.produto_id == 42
        assert p.descricao == "Arroz 5kg"
        assert p.preco == 25.90
        assert p.disponivel is True
        assert p.em_oferta is False
        assert p.oferta is None

    def test_from_api_with_offer(self):
        data = {
            "produto_id": 99,
            "descricao": "Leite 1L",
            "preco": 6.0,
            "unidade_sigla": "UN",
            "imagem": "leite.jpg",
            "disponivel": True,
            "quantidade_maxima": 20,
            "em_oferta": True,
            "oferta": {
                "oferta_id": 55,
                "nome": "Promo",
                "tag": "promo",
                "preco_oferta": 4.50,
                "preco_antigo": 6.0,
                "quantidade_minima": 2,
                "quantidade_maxima": 10,
            },
        }
        p = Produto.from_api(data)
        assert p.em_oferta is True
        assert p.oferta is not None
        assert p.oferta.preco_oferta == 4.50
        assert p.oferta.quantidade_minima == 2

    def test_from_api_empty_dict(self):
        p = Produto.from_api({})
        assert p.produto_id == 0
        assert p.descricao == ""
        assert p.preco == 0.0
        assert p.disponivel is False

    def test_from_api_extra_fields_ignored(self):
        data = {
            "produto_id": 1,
            "descricao": "X",
            "preco": 1.0,
            "unidade_sigla": "UN",
            "imagem": "",
            "disponivel": True,
            "quantidade_maxima": 1,
            "unknown_field": "ignored",
            "codigo_barras": "1234567890123",
            "sku": "SKU-001",
            "codigo_erp": 777,
        }
        p = Produto.from_api(data)
        assert p.codigo_barras == "1234567890123"
        assert p.sku == "SKU-001"
        assert p.codigo_erp == "777"


class TestCarrinhoItem:
    def test_defaults(self):
        item = CarrinhoItem(
            produto_id=1,
            nome="Test",
            preco_unit=5.0,
            quantidade=2,
            subtotal=10.0,
            un="UN",
            imagem="img.jpg",
        )
        assert item.em_oferta is False
        assert item.tag == ""


class TestListaCompras:
    def test_defaults(self):
        lista = ListaCompras(nome="My List")
        assert lista.itens == []
        assert lista.total == 0.0
        assert lista.criado_em == ""
        assert lista.cep == ""


class TestDepartamento:
    def test_defaults(self):
        d = Departamento(id=1, nome="Padaria")
        assert d.total_ofertas == 0
        assert d.total_produtos == 0
