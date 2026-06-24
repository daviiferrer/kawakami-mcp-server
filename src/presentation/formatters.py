from src.config import settings
from src.domain.models import CarrinhoItem, ListaCompras, Produto


def format_price(value: float) -> str:
    return f"R$ {value:.2f}".replace(".", ",")


def format_image_url(image_path: str) -> str:
    if image_path:
        return f"{settings.img_base_url}/{image_path}"
    return "N/A"


def format_product_card(p: Produto) -> str:
    preco = format_price(p.preco)
    disp = "SIM" if p.disponivel else "NAO"
    estoque = p.quantidade_maxima

    line = p.descricao
    line += f"\n  Preco: {preco} / {p.unidade_sigla}"

    if p.em_oferta and p.oferta:
        o = p.oferta
        line += f" | OFERTA: {format_price(o.preco_oferta)}"
        if o.preco_antigo > 0:
            line += f" ({o.desconto_pct:.0f}% OFF, era {format_price(o.preco_antigo)})"

    line += f"\n  Estoque: {estoque} | Disponivel: {disp}"
    line += f"\n  ID: {p.produto_id} | EAN: {p.codigo_barras}"
    line += f"\n  Imagem: {format_image_url(p.imagem)}"
    line += f"\n  Link: https://www.kawakami.com.br/produto/{p.produto_id}/{p.link}"
    return line


def format_search_results(termo: str, produtos: list[Produto], paginator: dict) -> str:
    total = paginator.get("total_items", len(produtos))
    page = paginator.get("page", 1)
    pages = paginator.get("total_pages", 1)

    lines = [f"=== BUSCA: '{termo}' ==="]
    lines.append(f"Total: {total} produtos | Pagina {page}/{pages}")
    lines.append("")

    for p in produtos:
        lines.append(format_product_card(p))
        lines.append("---")

    return "\n".join(lines)


def format_department_list(depts: list, cep: str) -> str:
    lines = ["=== DEPARTAMENTOS KAWAKAMI ===", f"Loja: CEP {cep}", ""]
    lines.append(f"{'ID':<5} {'Departamento':<30} {'Ofertas':>8}")
    lines.append("-" * 50)

    total_ofertas = 0
    for d in depts:
        lines.append(f"{d.id:<5} {d.nome:<30} {d.total_ofertas:>8}")
        total_ofertas += d.total_ofertas

    lines.append("-" * 50)
    lines.append(f"{'':<5} {'TOTAL DE OFERTAS':<30} {total_ofertas:>8}")
    return "\n".join(lines)


def format_department_products(
    dept_name: str, produtos: list[Produto], paginator: dict, apenas_ofertas: bool
) -> str:
    total = paginator.get("total_items", len(produtos))
    lines = [f"=== {dept_name.upper()} ==="]
    lines.append(f"Total: {total} produtos")
    if apenas_ofertas:
        lines.append("(Filtrado: apenas ofertas)")
    lines.append("")

    for p in produtos:
        preco = format_price(p.preco)
        line = p.descricao
        line += f" | Preco: {preco}/{p.unidade_sigla}"

        if p.em_oferta and p.oferta:
            line += f" | OFERTA: {format_price(p.oferta.preco_oferta)} [{p.oferta.tag}]"

        line += f" | Estoque: {p.quantidade_maxima} | Vendidos: {p.quantidade_vendida}"
        line += f"\n  EAN: {p.codigo_barras} | SKU: {p.sku} | ID: {p.produto_id}"
        line += f"\n  Imagem: {format_image_url(p.imagem)}"
        lines.append(line)
        lines.append("---")

    return "\n".join(lines)


def format_product_detail(p: Produto, dept_name: str) -> str:
    lines = [f"=== {p.descricao} ==="]
    lines.append(f"ID: {p.produto_id}")
    lines.append(f"Preco normal: {format_price(p.preco)} / {p.unidade_sigla}")
    lines.append(f"Imagem: {format_image_url(p.imagem)}")
    lines.append(f"EAN: {p.codigo_barras}")
    lines.append(f"SKU: {p.sku}")
    lines.append(f"Codigo ERP: {p.codigo_erp}")
    lines.append(f"Estoque: {p.quantidade_maxima} unidades")
    lines.append(f"Disponivel: {'SIM' if p.disponivel else 'NAO'}")
    lines.append(f"Vendidos: {p.quantidade_vendida}")
    lines.append(f"Departamento: {dept_name}")
    lines.append(f"Link: https://www.kawakami.com.br/produto/{p.produto_id}/{p.link}")

    if p.em_oferta and p.oferta:
        lines.append("")
        lines.append("--- OFERTA ATIVA ---")
        lines.append(f"Nome: {p.oferta.nome}")
        lines.append(f"Preco oferta: {format_price(p.oferta.preco_oferta)}")
        if p.oferta.preco_antigo > 0:
            old_price = format_price(p.oferta.preco_antigo)
            lines.append(f"Preco anterior: {old_price} ({p.oferta.desconto_pct:.0f}% OFF)")
        lines.append(f"Qtd minima: {p.oferta.quantidade_minima}")
        lines.append(f"Qtd maxima: {p.oferta.quantidade_maxima}")
        lines.append(f"Limite por cliente: {p.oferta.quantidade_maxima} unidades")

    return "\n".join(lines)


def format_offers_ranking(ofertas: list[Produto], cep: str) -> str:
    lines = [f"=== MELHORES OFERTAS DO DIA (CEP {cep}) ==="]
    lines.append(f"Total de ofertas encontradas: {len(ofertas)}")
    lines.append("")

    for i, o in enumerate(ofertas, 1):
        lines.append(f"{i}. {o.descricao} [{o.nome if hasattr(o, 'nome') else ''}]")
        oferta = o.oferta
        if oferta:
            offer_price = format_price(oferta.preco_oferta)
            old_price = format_price(oferta.preco_antigo)
            lines.append(f"   {offer_price} (era {old_price}, {oferta.desconto_pct:.0f}% OFF)")
            lines.append(
                f"   Tag: {oferta.tag} | Estoque: {o.quantidade_maxima} | ID: {o.produto_id}"
            )
            if o.imagem:
                lines.append(f"   Imagem: {format_image_url(o.imagem)}")
        lines.append("")

    return "\n".join(lines)


def format_cart(cart: list[CarrinhoItem]) -> str:
    if not cart:
        return "Carrinho vazio. Use 'adicionar_ao_carrinho' para começar."

    lines = ["CARRINHO DE COMPRAS", "=" * 50]
    total = 0.0

    for i, item in enumerate(cart, 1):
        tag = f" [{item.tag}]" if item.tag else ""
        lines.append(f"{i:>2}. {item.nome} ({item.quantidade}x)")
        lines.append(
            f"    {format_price(item.preco_unit)}/{item.un} = {format_price(item.subtotal)}{tag}"
        )
        total += item.subtotal

    lines.append("=" * 50)
    lines.append(f"TOTAL: {format_price(total)} ({len(cart)} itens)")
    return "\n".join(lines)


def format_saved_list(lista: ListaCompras) -> str:
    lines = [f"=== {lista.nome} ==="]
    lines.append(f"Criada em: {lista.criado_em} | CEP: {lista.cep}")
    lines.append("")

    for i, item in enumerate(lista.itens, 1):
        lines.append(f"{i}. {item.nome}")
        lines.append(f"   {format_price(item.preco_unit)} / {item.un}")
        if item.imagem:
            lines.append(f"   Imagem: {format_image_url(item.imagem)}")

    lines.append("")
    lines.append(f"TOTAL: {format_price(lista.total)}")
    return "\n".join(lines)


def format_saved_lists_summary(listas: dict[str, ListaCompras], sid: str) -> str:
    if not listas:
        return "Nenhuma lista salva nesta sessao. Use 'salvar_lista' para criar uma."

    lines = [f"=== MINHAS LISTAS (sessao: {sid}) ===", ""]
    for nome, lista in listas.items():
        lines.append(f"  {nome}")
        lines.append(f"    Itens: {len(lista.itens)} | Total: {format_price(lista.total)}")
        lines.append(f"    Criada: {lista.criado_em} | CEP: {lista.cep}")
        lines.append("")
    return "\n".join(lines)
