from mcp.server.fastmcp import FastMCP

from src.config import settings
from src.infrastructure.auth import token_manager
from src.infrastructure.vipcommerce_client import vip_client


token_manager.load()


def create_mcp(host: str = "0.0.0.0", port: int = 8000) -> FastMCP:
    mcp = FastMCP("Kawakami Supermercados", host=host, port=port)

    from src.tools.busca import buscar_produtos, buscar_por_ean
    from src.tools.catalogo import listar_departamentos, produtos_por_departamento, detalhes_produto
    from src.tools.ofertas import ofertas_do_dia, verificar_estoque
    from src.tools.carrinho import adicionar_ao_carrinho, ver_carrinho, remover_do_carrinho, limpar_carrinho
    from src.tools.listas import salvar_lista, minhas_listas, ver_lista, excluir_lista

    mcp.tool()(buscar_produtos)
    mcp.tool()(buscar_por_ean)
    mcp.tool()(listar_departamentos)
    mcp.tool()(produtos_por_departamento)
    mcp.tool()(detalhes_produto)
    mcp.tool()(ofertas_do_dia)
    mcp.tool()(verificar_estoque)
    mcp.tool()(adicionar_ao_carrinho)
    mcp.tool()(ver_carrinho)
    mcp.tool()(remover_do_carrinho)
    mcp.tool()(limpar_carrinho)
    mcp.tool()(salvar_lista)
    mcp.tool()(minhas_listas)
    mcp.tool()(ver_lista)
    mcp.tool()(excluir_lista)

    return mcp


async def health_check() -> dict:
    status = "ok"
    vip = "reachable"
    try:
        await vip_client.get_departments()
    except Exception:
        vip = "unreachable"
        status = "degraded"
    return {"status": status, "vip_commerce": vip}

