from src.config import settings
from src.infrastructure.vipcommerce_client import vip_client
from src.infrastructure.validation import sanitize_term, sanitize_cep
from src.infrastructure.error_handler import safe_tool
from src.presentation.formatters import format_search_results


@safe_tool
async def buscar_produtos(termo: str, cep: str = settings.default_cep, pagina: int = 1, limite: int = 50) -> str:
    termo = sanitize_term(termo)
    if not termo:
        return "Digite um termo de busca valido."
    cep = sanitize_cep(cep)
    limite = min(max(limite, 1), 100)
    produtos, paginator = await vip_client.search_products(termo, pagina)
    return format_search_results(termo, produtos[:limite], paginator)


@safe_tool
async def buscar_por_ean(codigo_barras: str, cep: str = settings.default_cep) -> str:
    codigo_barras = sanitize_term(codigo_barras)
    return await buscar_produtos(termo=codigo_barras, cep=cep, limite=5)
