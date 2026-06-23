from mcp.types import CallToolResult

from src.config import settings
from src.infrastructure.error_handler import safe_tool
from src.infrastructure.validation import sanitize_cep, validate_produto_id
from src.infrastructure.vipcommerce_client import vip_client
from src.presentation.formatters import (
    format_department_list,
    format_department_products,
    format_product_detail,
)
from src.presentation.structured import products_result


@safe_tool
async def listar_departamentos(cep: str = settings.default_cep) -> str:
    cep = sanitize_cep(cep)
    depts = await vip_client.get_departments(cep=cep)
    return format_department_list(depts, cep)


@safe_tool
async def produtos_por_departamento(
    departamento_id: int,
    cep: str = settings.default_cep,
    limite: int = 100,
    apenas_ofertas: bool = False,
) -> CallToolResult:
    cep = sanitize_cep(cep)
    limite = min(max(limite, 1), 500)
    dept_name = f"Departamento {departamento_id}"
    produtos, paginator = await vip_client.get_products_by_department(
        departamento_id,
        limite,
        apenas_ofertas,
        cep,
    )
    visible_products = produtos[:limite]
    text = format_department_products(
        dept_name,
        visible_products,
        paginator,
        apenas_ofertas,
    )
    return products_result(
        text,
        key=f"department-{departamento_id}",
        title=dept_name,
        products=visible_products,
    )


@safe_tool
async def detalhes_produto(
    produto_id: int,
    cep: str = settings.default_cep,
) -> CallToolResult | str:
    if not validate_produto_id(produto_id):
        return f"ID de produto invalido: {produto_id}"
    cep = sanitize_cep(cep)
    p = await vip_client.get_product_by_id(produto_id, cep=cep)
    if not p:
        return f"Produto ID {produto_id} nao encontrado nos departamentos disponiveis."
    text = format_product_detail(p, p.dept_name or "N/A")
    return products_result(
        text,
        key=f"product-{produto_id}",
        title="Detalhes do Produto",
        products=[p],
    )
