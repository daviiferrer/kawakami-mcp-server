from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context
from mcp.types import CallToolResult

from src.config import settings
from src.domain.models import CarrinhoItem
from src.infrastructure.auth_required import extract_request, require_auth
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.infrastructure.validation import sanitize_cep, sanitize_term, validate_quantidade
from src.infrastructure.vipcommerce_client import vip_client
from src.presentation.formatters import format_cart, format_price
from src.presentation.structured import cart_result


@safe_tool
async def adicionar_ao_carrinho(
    session_id: str,
    termo: str = "",
    cep: str = settings.default_cep,
    quantidade: int = 1,
    itens: list[dict[str, Any]] | None = None,
    modo: str = "adicionar",
    ctx: Context = None,
) -> CallToolResult | str:
    auth_err = require_auth(extract_request(ctx))
    if auth_err is not None:
        return auth_err

    session_store.require_session(session_id)
    cep = sanitize_cep(cep)

    if itens is not None and len(itens) > 0:
        return await _batch_add(session_id, cep, itens, modo)

    termo = sanitize_term(termo)
    if not termo:
        return "Informe o termo de busca ou a lista de itens para adicionar ao carrinho."

    quantidade = validate_quantidade(quantidade)
    produtos, _ = await vip_client.search_products(termo, page=1, cep=cep)
    if not produtos:
        return f"Nenhum produto encontrado para '{termo}'."

    best = next((product for product in produtos if product.disponivel), produtos[0])
    item = CarrinhoItem.from_produto(best, quantidade)
    cart = session_store.add_to_cart(session_id, item)
    total = CarrinhoItem.total(cart)
    tag_text = f" [{item.tag}]" if item.tag else ""
    text = (
        f"+ {item.nome} ({quantidade}x) - {format_price(item.subtotal)}{tag_text}\n"
        f"Carrinho: {len(cart)} itens - {format_price(total)}"
    )
    return cart_result(text, session_id=session_id, cart=cart)


async def _batch_add(
    session_id: str,
    cep: str,
    itens: list[dict[str, Any]],
    modo: str,
) -> CallToolResult:
    if modo == "substituir":
        session_store.clear_cart(session_id)

    adicionados: list[str] = []
    falharam: list[dict[str, Any]] = []

    for entry in itens:
        produto_id = int(entry.get("produto_id", 0))
        qtd = int(entry.get("quantidade", 1))
        if produto_id <= 0 or qtd <= 0:
            falharam.append(
                {
                    "produto_id": produto_id,
                    "quantidade": qtd,
                    "motivo": "produto_id ou quantidade invalidos",
                }
            )
            continue

        nome = entry.get("nome", "")
        preco_unit = entry.get("preco_unit") or entry.get("preco_unitario") or entry.get("preco")
        un = entry.get("un", "UN")
        imagem = entry.get("imagem", "")
        em_oferta = bool(entry.get("em_oferta"))
        tag = entry.get("tag", "")

        if nome and preco_unit is not None:
            item = CarrinhoItem(
                produto_id=produto_id,
                nome=str(nome),
                preco_unit=float(preco_unit),
                quantidade=qtd,
                subtotal=round(float(preco_unit) * qtd, 2),
                un=str(un),
                imagem=str(imagem),
                em_oferta=em_oferta,
                tag=str(tag),
            )
            session_store.add_to_cart(session_id, item)
            adicionados.append(f"{nome} ({qtd}x)")
            continue

        try:
            product = await vip_client.get_product_by_id(produto_id, cep=cep)
        except Exception as exc:
            falharam.append({"produto_id": produto_id, "quantidade": qtd, "motivo": str(exc)})
            continue

        if product is None:
            falharam.append(
                {
                    "produto_id": produto_id,
                    "quantidade": qtd,
                    "motivo": f"produto {produto_id} nao encontrado",
                }
            )
            continue

        item = CarrinhoItem.from_produto(product, qtd)
        session_store.add_to_cart(session_id, item)
        adicionados.append(f"{product.descricao} ({qtd}x)")

    cart = session_store.get_cart(session_id)
    total = CarrinhoItem.total(cart)

    lines = [f"Adicionados: {len(adicionados)} itens"]
    if falharam:
        lines.append(f"Falhas: {len(falharam)} itens - {', '.join(f['motivo'] for f in falharam)}")
    lines.append(f"Total: {format_price(total)} ({len(cart)} itens no carrinho)")
    return cart_result("\n".join(lines), session_id=session_id, cart=cart)


@safe_tool
async def ver_carrinho(session_id: str, ctx: Context = None) -> CallToolResult:
    auth_err = require_auth(extract_request(ctx))
    if auth_err is not None:
        return auth_err
    cart = session_store.get_cart(session_id)
    return cart_result(format_cart(cart), session_id=session_id, cart=cart)


@safe_tool
async def remover_do_carrinho(
    session_id: str, termo: str, ctx: Context = None
) -> CallToolResult | str:
    auth_err = require_auth(extract_request(ctx))
    if auth_err is not None:
        return auth_err
    termo = sanitize_term(termo)
    if not termo:
        return "Digite o nome do produto a remover."

    session_store.require_session(session_id)
    removed = session_store.remove_from_cart(session_id, termo)
    if removed is None:
        cart = session_store.get_cart(session_id)
        matches = [item for item in cart if termo.lower() in item.nome.lower()]
        if not matches:
            return f"Nenhum item com '{termo}' no carrinho."
        names = ", ".join(item.nome for item in matches)
        return f"Multiplos itens com '{termo}': {names}. Seja mais especifico."

    cart = session_store.get_cart(session_id)
    total = CarrinhoItem.total(cart)
    text = f"- {removed.nome}\nCarrinho: {len(cart)} itens - {format_price(total)}"
    return cart_result(text, session_id=session_id, cart=cart)


@safe_tool
async def limpar_carrinho(session_id: str, ctx: Context = None) -> CallToolResult:
    auth_err = require_auth(extract_request(ctx))
    if auth_err is not None:
        return auth_err
    session_store.clear_cart(session_id)
    return cart_result("Carrinho esvaziado.", session_id=session_id, cart=[])
