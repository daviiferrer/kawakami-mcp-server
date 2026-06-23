from __future__ import annotations

import asyncio
from typing import Any

from mcp.types import CallToolResult
from mcp.server.fastmcp import Context

from src.config import settings
from src.domain.models import CarrinhoItem
from src.infrastructure.auth_required import require_auth
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
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
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
    price = best.preco_efetivo
    tag = best.oferta.tag if best.oferta else ""
    item = CarrinhoItem(
        produto_id=best.produto_id,
        nome=best.descricao,
        preco_unit=price,
        quantidade=quantidade,
        subtotal=round(price * quantidade, 2),
        un=best.unidade_sigla,
        imagem=best.imagem,
        em_oferta=best.em_oferta,
        tag=tag,
    )
    cart = session_store.add_to_cart(session_id, item)
    total = sum(cart_item.subtotal for cart_item in cart)
    tag_text = f" [{tag}]" if tag else ""
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

    async def resolve(item: dict[str, Any]) -> tuple[int, int, str | None]:
        produto_id = int(item.get("produto_id", 0))
        qtd = int(item.get("quantidade", 1))
        if produto_id <= 0 or qtd <= 0:
            return produto_id, qtd, "produto_id ou quantidade invalidos"
        product = await vip_client.get_product_by_id(produto_id, cep=cep)
        if product is None:
            return produto_id, qtd, f"produto {produto_id} nao encontrado"
        price = product.preco_efetivo
        tag = product.oferta.tag if product.oferta else ""
        cart_item = CarrinhoItem(
            produto_id=product.produto_id,
            nome=product.descricao,
            preco_unit=price,
            quantidade=qtd,
            subtotal=round(price * qtd, 2),
            un=product.unidade_sigla,
            imagem=product.imagem,
            em_oferta=product.em_oferta,
            tag=tag,
        )
        session_store.add_to_cart(session_id, cart_item)
        adicionados.append(f"{product.descricao} ({qtd}x)")
        return produto_id, qtd, None

    tasks = [resolve(item) for item in itens]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, result in enumerate(results):
        if isinstance(result, BaseException):
            item = itens[idx]
            falharam.append({
                "produto_id": item.get("produto_id", 0),
                "quantidade": item.get("quantidade", 1),
                "motivo": str(result),
            })
            continue
        pid, qtd, err = result
        if err:
            falharam.append({"produto_id": pid, "quantidade": qtd, "motivo": err})

    cart = session_store.get_cart(session_id)
    total = sum(ci.subtotal for ci in cart)

    lines = [f"Adicionados: {len(adicionados)} itens"]
    if falharam:
        lines.append(f"Falhas: {len(falharam)} itens - {', '.join(f['motivo'] for f in falharam)}")
    lines.append(f"Total: {format_price(total)} ({len(cart)} itens no carrinho)")
    return cart_result("\n".join(lines), session_id=session_id, cart=cart)


@safe_tool
async def ver_carrinho(session_id: str, ctx: Context = None) -> CallToolResult:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err
    cart = session_store.get_cart(session_id)
    return cart_result(format_cart(cart), session_id=session_id, cart=cart)


@safe_tool
async def remover_do_carrinho(session_id: str, termo: str, ctx: Context = None) -> CallToolResult | str:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
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
    total = sum(item.subtotal for item in cart)
    text = f"- {removed.nome}\nCarrinho: {len(cart)} itens - {format_price(total)}"
    return cart_result(text, session_id=session_id, cart=cart)


@safe_tool
async def limpar_carrinho(session_id: str, ctx: Context = None) -> CallToolResult:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err
    session_store.clear_cart(session_id)
    return cart_result("Carrinho esvaziado.", session_id=session_id, cart=[])
