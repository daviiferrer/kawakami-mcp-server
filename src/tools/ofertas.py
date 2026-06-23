from src.config import settings
from src.infrastructure.vipcommerce_client import vip_client
from src.infrastructure.validation import sanitize_cep, validate_produto_id
from src.infrastructure.error_handler import safe_tool
from src.presentation.formatters import format_offers_ranking


@safe_tool
async def ofertas_do_dia(cep: str = settings.default_cep, limite: int = 50) -> str:
    cep = sanitize_cep(cep)
    limite = min(max(limite, 1), 100)
    ofertas = await vip_client.get_best_offers(limite)
    return format_offers_ranking(ofertas, cep)


@safe_tool
async def verificar_estoque(produto_id: int, cep: str = settings.default_cep) -> str:
    from src.tools.catalogo import detalhes_produto
    if not validate_produto_id(produto_id):
        return f"ID de produto invalido: {produto_id}"
    result = await detalhes_produto(produto_id, cep)
    if "nao encontrado" in result.lower():
        return f"Produto {produto_id} nao encontrado."
    return result
