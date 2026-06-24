import asyncio
import time

from mcp.server.fastmcp import Context

from src.config import settings
from src.domain.models import CarrinhoItem, ListaCompras
from src.infrastructure.auth_required import require_auth
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.session_store import session_store
from src.infrastructure.validation import sanitize_term, validate_nome_lista
from src.infrastructure.vipcommerce_client import vip_client
from src.presentation.formatters import format_price, format_saved_list, format_saved_lists_summary

_sem = asyncio.Semaphore(5)


async def _resolve_item(item: str, cep: str):
    produtos, _ = await vip_client.search_products(item, page=1, cep=cep)
    if not produtos:
        return None
    best = next((p for p in produtos if p.disponivel), produtos[0])
    return CarrinhoItem(
        produto_id=best.produto_id,
        nome=best.descricao,
        preco_unit=best.preco_efetivo,
        quantidade=1,
        subtotal=best.preco_efetivo,
        un=best.unidade_sigla,
        imagem=best.imagem,
        em_oferta=best.em_oferta,
        tag=best.oferta.tag if best.oferta else "",
    )


async def _resolve_safe(item: str, cep: str):
    async with _sem:
        return await _resolve_item(item, cep)


@safe_tool
async def salvar_lista(
    session_id: str,
    nome: str,
    itens: str,
    cep: str = settings.default_cep,
    ctx: Context = None,
) -> str:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err.content[0].text
    nome = validate_nome_lista(nome)
    items_raw = [sanitize_term(i) for i in itens.split(",") if i.strip()]
    items_list = [i for i in items_raw if i]
    if not items_list:
        return "Forneca pelo menos um item para a lista."
    session_store.require_session(session_id)
    tasks = [_resolve_safe(item, cep) for item in items_list]
    results = await asyncio.gather(*tasks)
    saved_items = [r for r in results if r is not None]
    total = sum(item.subtotal for item in saved_items)
    lista = ListaCompras(
        nome=nome,
        itens=saved_items,
        total=total,
        criado_em=time.strftime("%d/%m/%Y %H:%M"),
        cep=cep,
    )
    session_store.save_list(session_id, nome, lista)
    return (
        f"Lista '{nome}' salva com {len(saved_items)} itens. Total estimado: {format_price(total)}"
    )


@safe_tool
async def minhas_listas(session_id: str, ctx: Context = None) -> str:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err.content[0].text
    listas = session_store.get_all_lists(session_id)
    return format_saved_lists_summary(listas, session_id)


@safe_tool
async def ver_lista(session_id: str, nome: str, ctx: Context = None) -> str:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err.content[0].text
    nome = validate_nome_lista(nome)
    lista = session_store.get_list(session_id, nome)
    if not lista:
        return f"Lista '{nome}' nao encontrada."
    return format_saved_list(lista)


@safe_tool
async def excluir_lista(session_id: str, nome: str, ctx: Context = None) -> str:
    request = ctx.request_context.request if ctx and ctx.request_context else None
    auth_err = require_auth(request)
    if auth_err is not None:
        return auth_err.content[0].text
    nome = validate_nome_lista(nome)
    if session_store.delete_list(session_id, nome):
        return f"Lista '{nome}' excluida."
    return f"Lista '{nome}' nao encontrada."

