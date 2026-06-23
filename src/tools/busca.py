from mcp.types import CallToolResult

from src.config import settings
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.validation import sanitize_cep, sanitize_term
from src.infrastructure.vipcommerce_client import vip_client
from src.presentation.formatters import format_search_results
from src.presentation.structured import products_result


@safe_tool
async def buscar_produtos(
    termo: str,
    cep: str = settings.default_cep,
    pagina: int = 1,
    limite: int = 50,
) -> CallToolResult | str:
    termo = sanitize_term(termo)
    if not termo:
        return "Digite um termo de busca valido."
    cep = sanitize_cep(cep)
    limite = min(max(limite, 1), 100)
    produtos, paginator = await vip_client.search_products(termo, pagina, cep=cep)
    visible_products = produtos[:limite]
    text = format_search_results(termo, visible_products, paginator)
    return products_result(
        text,
        key=f"search-{termo}",
        title=f"Busca: {termo}",
        products=visible_products,
    )


@safe_tool
async def buscar_por_ean(
    codigo_barras: str,
    cep: str = settings.default_cep,
) -> CallToolResult | str:
    codigo_barras = sanitize_term(codigo_barras)
    return await buscar_produtos(termo=codigo_barras, cep=cep, limite=5)
