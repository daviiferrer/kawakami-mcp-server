from src.config import settings
from src.infrastructure.vipcommerce_client import vip_client
from src.infrastructure.session_store import session_store
from src.infrastructure.validation import sanitize_term, sanitize_cep, validate_quantidade
from src.infrastructure.error_handler import safe_tool
from src.domain.models import CarrinhoItem
from src.presentation.formatters import format_price, format_cart


@safe_tool
async def adicionar_ao_carrinho(termo: str, ctx, cep: str = settings.default_cep, quantidade: int = 1) -> str:
    termo = sanitize_term(termo)
    if not termo:
        return "Digite um produto valido para adicionar ao carrinho."
    cep = sanitize_cep(cep)
    quantidade = validate_quantidade(quantidade)
    sid = session_store.get_session_id(getattr(ctx, "session_id", None))
    produtos, _ = await vip_client.search_products(termo, page=1)
    if not produtos:
        return f"Nenhum produto encontrado para '{termo}'."
    best = next((p for p in produtos if p.disponivel), produtos[0])
    preco = best.preco_efetivo
    tag = best.oferta.tag if best.oferta else ""
    item = CarrinhoItem(
        produto_id=best.produto_id,
        nome=best.descricao,
        preco_unit=preco,
        quantidade=quantidade,
        subtotal=round(preco * quantidade, 2),
        un=best.unidade_sigla,
        imagem=best.imagem,
        em_oferta=best.em_oferta,
        tag=tag,
    )
    cart = session_store.add_to_cart(sid, item)
    total = sum(i.subtotal for i in cart)
    tag_str = f" [{tag}]" if tag else ""
    return f"+ {item.nome} ({quantidade}x) — {format_price(item.subtotal)}{tag_str}\nCarrinho: {len(cart)} itens — {format_price(total)}"


@safe_tool
async def ver_carrinho(ctx) -> str:
    sid = session_store.get_session_id(getattr(ctx, "session_id", None))
    cart = session_store.get_cart(sid)
    return format_cart(cart)


@safe_tool
async def remover_do_carrinho(termo: str, ctx) -> str:
    termo = sanitize_term(termo)
    if not termo:
        return "Digite o nome do produto a remover."
    sid = session_store.get_session_id(getattr(ctx, "session_id", None))
    removed = session_store.remove_from_cart(sid, termo)
    if removed is None:
        cart = session_store.get_cart(sid)
        matches = [i for i in cart if termo.lower() in i.nome.lower()]
        if not matches:
            return f"Nenhum item com '{termo}' no carrinho."
        names = ", ".join(m["nome"] for m in matches)
        return f"Multiplos itens com '{termo}': {names}. Seja mais especifico."
    cart = session_store.get_cart(sid)
    total = sum(i.subtotal for i in cart)
    return f"- {removed.nome}\nCarrinho: {len(cart)} itens — {format_price(total)}"


@safe_tool
async def limpar_carrinho(ctx) -> str:
    sid = session_store.get_session_id(getattr(ctx, "session_id", None))
    session_store.clear_cart(sid)
    return "Carrinho esvaziado."
