from mcp.types import CallToolResult

from src.config import settings
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.validation import clamp_limit, sanitize_cep, validate_produto_id
from src.infrastructure.vipcommerce_client import vip_client
from src.presentation.formatters import format_offers_ranking
from src.presentation.structured import products_result


@safe_tool
async def ofertas_do_dia(
    cep: str = settings.default_cep,
    limite: int = 50,
) -> CallToolResult:
    cep = sanitize_cep(cep)
    limite = clamp_limit(limite)
    ofertas = await vip_client.get_best_offers(limite, cep=cep)
    text = format_offers_ranking(ofertas, cep)
    return products_result(
        text,
        key="offers",
        title="Ofertas do Dia",
        products=ofertas,
    )


@safe_tool
async def verificar_estoque(
    produto_id: int,
    cep: str = settings.default_cep,
) -> CallToolResult | str:
    from src.tools.catalogo import detalhes_produto

    if not validate_produto_id(produto_id):
        return f"ID de produto invalido: {produto_id}"
    result = await detalhes_produto(produto_id, cep)
    if isinstance(result, str) and "nao encontrado" in result.lower():
        return f"Produto {produto_id} nao encontrado."
    return result
