from src.domain.models import CarrinhoItem, Departamento, ListaCompras, Oferta, Produto
from src.presentation.formatters import (
    format_cart,
    format_department_list,
    format_department_products,
    format_offers_ranking,
    format_product_detail,
    format_saved_list,
    format_saved_lists_summary,
    format_search_results,
)


def _make_produto(*, offer: bool = False, disponivel: bool = True) -> Produto:
    oferta = None
    if offer:
        oferta = Oferta(
            oferta_id=1,
            nome="Promo",
            tag="promo-tag",
            preco_oferta=7.0,
            preco_antigo=10.0,
        )
    return Produto(
        produto_id=42,
        descricao="Arroz 5kg",
        preco=10.0,
        unidade_sigla="KG",
        imagem="arroz.jpg",
        disponivel=disponivel,
        quantidade_maxima=100,
        codigo_barras="7891000000001",
        sku="SKU-42",
        codigo_erp="ERP-42",
        quantidade_vendida=50,
        link="arroz-5kg",
        secao_id=3,
        em_oferta=offer,
        oferta=oferta,
    )


class TestFormatSearchResults:
    def test_basic_output(self):
        p = _make_produto()
        paginator = {"total_items": 1, "page": 1, "total_pages": 1}
        result = format_search_results("arroz", [p], paginator)
        assert "BUSCA: 'arroz'" in result
        assert "Total: 1 produtos" in result
        assert "Arroz 5kg" in result

    def test_multi_page(self):
        p = _make_produto()
        paginator = {"total_items": 25, "page": 2, "total_pages": 3}
        result = format_search_results("arroz", [p], paginator)
        assert "Pagina 2/3" in result

    def test_empty_results(self):
        paginator = {"total_items": 0, "page": 1, "total_pages": 1}
        result = format_search_results("xyz", [], paginator)
        assert "BUSCA: 'xyz'" in result
        assert "Total: 0 produtos" in result


class TestFormatDepartmentList:
    def test_basic_output(self):
        depts = [
            Departamento(id=1, nome="Padaria", total_ofertas=5),
            Departamento(id=2, nome="Acougue", total_ofertas=3),
        ]
        result = format_department_list(depts, "19700000")
        assert "DEPARTAMENTOS KAWAKAMI" in result
        assert "CEP 19700000" in result
        assert "Padaria" in result
        assert "Acougue" in result
        assert "TOTAL DE OFERTAS" in result

    def test_empty_departments(self):
        result = format_department_list([], "19700000")
        assert "DEPARTAMENTOS KAWAKAMI" in result


class TestFormatDepartmentProducts:
    def test_basic_output(self):
        p = _make_produto()
        paginator = {"total_items": 1}
        result = format_department_products("Padaria", [p], paginator, False)
        assert "PADARIA" in result
        assert "Arroz 5kg" in result
        assert "Estoque: 100" in result
        assert "Vendidos: 50" in result

    def test_offers_only_filter(self):
        p = _make_produto(offer=True)
        paginator = {"total_items": 1}
        result = format_department_products("Padaria", [p], paginator, True)
        assert "apenas ofertas" in result
        assert "OFERTA" in result

    def test_product_without_image(self):
        p = _make_produto()
        p.imagem = ""
        result = format_department_products("X", [p], {"total_items": 1}, False)
        assert "N/A" in result


class TestFormatProductDetail:
    def test_basic_detail(self):
        p = _make_produto()
        result = format_product_detail(p, "Mercearia")
        assert "=== Arroz 5kg ===" in result
        assert "ID: 42" in result
        assert "R$ 10,00" in result
        assert "EAN: 7891000000001" in result
        assert "SKU: SKU-42" in result
        assert "Departamento: Mercearia" in result
        assert "Disponivel: SIM" in result

    def test_detail_with_offer(self):
        p = _make_produto(offer=True)
        result = format_product_detail(p, "Mercearia")
        assert "OFERTA ATIVA" in result
        assert "Promo" in result
        assert "R$ 7,00" in result
        assert "30% OFF" in result

    def test_detail_unavailable(self):
        p = _make_produto(disponivel=False)
        result = format_product_detail(p, "")
        assert "Disponivel: NAO" in result


class TestFormatOffersRanking:
    def test_basic_ranking(self):
        p = _make_produto(offer=True)
        result = format_offers_ranking([p], "19700000")
        assert "MELHORES OFERTAS DO DIA" in result
        assert "CEP 19700000" in result
        assert "Arroz 5kg" in result
        assert "R$ 7,00" in result
        assert "30% OFF" in result

    def test_empty_offers(self):
        result = format_offers_ranking([], "19700000")
        assert "Total de ofertas encontradas: 0" in result


class TestFormatCart:
    def test_empty_cart(self):
        result = format_cart([])
        assert "Carrinho vazio" in result

    def test_cart_with_items(self):
        items = [
            CarrinhoItem(
                produto_id=1,
                nome="Arroz",
                preco_unit=25.0,
                quantidade=2,
                subtotal=50.0,
                un="KG",
                imagem="",
            ),
            CarrinhoItem(
                produto_id=2,
                nome="Feijao",
                preco_unit=8.0,
                quantidade=1,
                subtotal=8.0,
                un="KG",
                imagem="",
                tag="promo",
            ),
        ]
        result = format_cart(items)
        assert "CARRINHO DE COMPRAS" in result
        assert "Arroz (2x)" in result
        assert "Feijao (1x)" in result
        assert "[promo]" in result
        assert "TOTAL: R$ 58,00 (2 itens)" in result


class TestFormatSavedList:
    def test_basic_list(self):
        lista = ListaCompras(
            nome="Semanal",
            itens=[
                CarrinhoItem(
                    produto_id=1,
                    nome="Leite",
                    preco_unit=5.0,
                    quantidade=1,
                    subtotal=5.0,
                    un="UN",
                    imagem="leite.jpg",
                ),
            ],
            total=5.0,
            criado_em="01/01/2025 10:00",
            cep="19700000",
        )
        result = format_saved_list(lista)
        assert "=== Semanal ===" in result
        assert "Leite" in result
        assert "R$ 5,00" in result
        assert "01/01/2025" in result


class TestFormatSavedListsSummary:
    def test_empty_lists(self):
        result = format_saved_lists_summary({}, "abc123")
        assert "Nenhuma lista salva" in result

    def test_with_lists(self):
        lista = ListaCompras(
            nome="Semanal",
            itens=[
                CarrinhoItem(
                    produto_id=1,
                    nome="X",
                    preco_unit=10.0,
                    quantidade=1,
                    subtotal=10.0,
                    un="UN",
                    imagem="",
                ),
            ],
            total=10.0,
            criado_em="01/01/2025",
            cep="19700000",
        )
        result = format_saved_lists_summary({"Semanal": lista}, "sess-1")
        assert "MINHAS LISTAS" in result
        assert "sess-1" in result
        assert "Semanal" in result
        assert "Itens: 1" in result
