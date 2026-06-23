from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import settings
from src.infrastructure.auth import token_manager
from src.presentation.widget import (
    WIDGET_MIME_TYPE,
    WIDGET_RESOURCE_META,
    WIDGET_TOOL_META,
    WIDGET_URI,
    load_widget_html,
)

token_manager.load()


def create_mcp(host: str = "0.0.0.0", port: int = 8000) -> FastMCP:
    mcp = FastMCP(
        "Kawakami Supermercados",
        host=host,
        port=port,
        instructions="Servidor MCP do Supermercados Kawakami. Busque produtos, compare precos, "
        "monte carrinho de compras e salve listas. CEP padrao: 19700000 (Paraguacu Paulista).",
    )

    from src.infrastructure.sessions import criar_sessao
    from src.tools.busca import buscar_por_ean, buscar_produtos
    from src.tools.carrinho import (
        adicionar_ao_carrinho,
        limpar_carrinho,
        remover_do_carrinho,
        ver_carrinho,
    )
    from src.tools.catalogo import detalhes_produto, listar_departamentos, produtos_por_departamento
    from src.tools.listas import excluir_lista, minhas_listas, salvar_lista, ver_lista
    from src.tools.ofertas import ofertas_do_dia, verificar_estoque

    read_only = ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
    write = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
    destructive = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
    create = ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )

    mcp.tool(
        title="Criar sessão de compras",
        description="Use esta tool antes de manipular carrinho ou listas.",
        annotations=create,
        structured_output=False,
    )(criar_sessao)
    mcp.tool(
        title="Buscar produtos",
        description="Use esta tool para buscar produtos Kawakami por nome.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(buscar_produtos)
    mcp.tool(
        title="Buscar produto por EAN",
        description="Use esta tool para buscar um produto pelo código de barras EAN.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(buscar_por_ean)
    mcp.tool(
        title="Listar departamentos",
        description="Use esta tool para consultar os departamentos disponíveis.",
        annotations=read_only,
    )(listar_departamentos)
    mcp.tool(
        title="Produtos por departamento",
        description="Use esta tool para listar produtos de um departamento Kawakami.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(produtos_por_departamento)
    mcp.tool(
        title="Detalhes do produto",
        description="Use esta tool para consultar um produto Kawakami pelo ID.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(detalhes_produto)
    mcp.tool(
        title="Ofertas do dia",
        description="Use esta tool para consultar as melhores ofertas Kawakami.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(ofertas_do_dia)
    mcp.tool(
        title="Verificar estoque",
        description="Use esta tool para consultar estoque e detalhes de um produto.",
        annotations=read_only,
        meta=WIDGET_TOOL_META,
        structured_output=False,
    )(verificar_estoque)
    mcp.tool(
        title="Adicionar ao carrinho",
        description="Use esta tool para definir a quantidade de um produto no carrinho.",
        annotations=write,
        structured_output=False,
    )(adicionar_ao_carrinho)
    mcp.tool(
        title="Ver carrinho",
        description="Use esta tool para consultar o carrinho de uma sessão.",
        annotations=read_only,
        structured_output=False,
    )(ver_carrinho)
    mcp.tool(
        title="Remover do carrinho",
        description="Use esta tool para remover um produto do carrinho.",
        annotations=destructive,
        structured_output=False,
    )(remover_do_carrinho)
    mcp.tool(
        title="Limpar carrinho",
        description="Use esta tool para remover todos os produtos do carrinho.",
        annotations=destructive,
        structured_output=False,
    )(limpar_carrinho)
    mcp.tool(
        title="Salvar lista",
        description="Use esta tool para criar ou substituir uma lista de compras.",
        annotations=write,
    )(salvar_lista)
    mcp.tool(
        title="Listar listas salvas",
        description="Use esta tool para consultar as listas de uma sessão.",
        annotations=read_only,
    )(minhas_listas)
    mcp.tool(
        title="Ver lista salva",
        description="Use esta tool para consultar os itens de uma lista salva.",
        annotations=read_only,
    )(ver_lista)
    mcp.tool(
        title="Excluir lista",
        description="Use esta tool para excluir uma lista salva.",
        annotations=destructive,
    )(excluir_lista)

    @mcp.resource(
        WIDGET_URI,
        name="kawakami-catalog",
        title="Kawakami Catalog",
        description="Widget interativo de produtos e carrinho.",
        mime_type=WIDGET_MIME_TYPE,
        meta=WIDGET_RESOURCE_META,
    )
    def catalog_widget() -> str:
        return load_widget_html()

    @mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
    async def health_check(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    if settings.auth0_domain:
        @mcp.custom_route(
            "/.well-known/oauth-protected-resource",
            methods=["GET"],
            include_in_schema=False,
        )
        async def oauth_metadata(_: Request) -> JSONResponse:
            return JSONResponse({
                "resource": settings.auth0_audience or "https://kawakami.axischat.com.br",
                "authorization_servers": [f"https://{settings.auth0_domain}/"],
                "scopes_supported": ["cart:read", "cart:write"],
            })
        @mcp.custom_route(
            "/.well-known/oauth-protected-resource/mcp",
            methods=["GET"],
            include_in_schema=False,
        )
        async def oauth_metadata_mcp(_: Request) -> JSONResponse:
            return JSONResponse({
                "resource": settings.auth0_audience or "https://kawakami.axischat.com.br",
                "authorization_servers": [f"https://{settings.auth0_domain}/"],
                "scopes_supported": ["cart:read", "cart:write"],
            })

    return mcp
