from src.config import settings
from src.infrastructure.vipcommerce_client import vip_client
from src.infrastructure.validation import sanitize_cep, validate_produto_id
from src.infrastructure.error_handler import safe_tool
from src.presentation.formatters import (
    format_department_list,
    format_department_products,
    format_product_detail,
)


@safe_tool
async def listar_departamentos(cep: str = settings.default_cep) -> str:
    cep = sanitize_cep(cep)
    depts = await vip_client.get_departments()
    return format_department_list(depts, cep)


@safe_tool
async def produtos_por_departamento(departamento_id: int, cep: str = settings.default_cep, limite: int = 100, apenas_ofertas: bool = False) -> str:
    cep = sanitize_cep(cep)
    limite = min(max(limite, 1), 500)
    depts = await vip_client.get_departments()
    dept_name = f"Departamento {departamento_id}"
    for d in depts:
        if d.id == departamento_id:
            dept_name = d.nome
            break
    produtos, paginator = await vip_client.get_products_by_department(departamento_id, limite, apenas_ofertas)
    return format_department_products(dept_name, produtos[:limite], paginator, apenas_ofertas)


@safe_tool
async def detalhes_produto(produto_id: int, cep: str = settings.default_cep) -> str:
    if not validate_produto_id(produto_id):
        return f"ID de produto invalido: {produto_id}"
    cep = sanitize_cep(cep)
    depts = await vip_client.get_departments()
    dept_name = "N/A"
    p = await vip_client.get_product_by_id(produto_id)
    if not p:
        return f"Produto ID {produto_id} nao encontrado nos departamentos disponiveis."
    for d in depts:
        if d.id == p.secao_id:
            dept_name = d.nome
            break
    return format_product_detail(p, dept_name)
