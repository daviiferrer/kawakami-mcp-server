from typing import Any

from mcp.types import CallToolResult, TextContent

from src.domain.models import CarrinhoItem, Produto


def _tag_kind(tag: str) -> str | None:
    normalized = tag.lower()
    if "exclus" in normalized or "app" in normalized:
        return "exclusive"
    if "clube" in normalized or "amigo" in normalized:
        return "club"
    if normalized:
        return "weekly"
    return None


def product_to_ui(product: Produto) -> dict[str, Any]:
    """Converte um produto de domínio para o contrato da UI."""
    offer = product.oferta
    return {
        "id": product.produto_id,
        "name": product.descricao,
        "price": product.preco,
        "offerPrice": offer.preco_oferta if offer else None,
        "originalPrice": offer.preco_antigo if offer else None,
        "unit": product.unidade_sigla,
        "image": product.imagem,
        "stock": product.quantidade_maxima,
        "tag": _tag_kind(offer.tag) if offer else None,
        "tagLabel": offer.nome if offer else None,
    }


def products_result(
    text: str,
    *,
    key: str,
    title: str,
    products: list[Produto],
) -> CallToolResult:
    """Cria resultado textual e estruturado para listas de produtos."""
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent={
            "sections": [
                {
                    "key": key,
                    "title": title,
                    "products": [product_to_ui(product) for product in products],
                }
            ]
        },
    )


def cart_result(
    text: str,
    *,
    session_id: str,
    cart: list[CarrinhoItem],
) -> CallToolResult:
    """Cria snapshot autoritativo do carrinho após uma operação."""
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent={
            "sessionId": session_id,
            "cart": [
                {
                    "id": item.produto_id,
                    "name": item.nome,
                    "unit": item.un,
                    "unitPrice": item.preco_unit,
                    "quantity": item.quantidade,
                    "subtotal": item.subtotal,
                    "image": item.imagem,
                    "isOffer": item.em_oferta,
                    "originalPrice": None,
                }
                for item in cart
            ],
        },
    )


def session_result(session_id: str) -> CallToolResult:
    """Retorna um identificador de sessão explícito."""
    return CallToolResult(
        content=[TextContent(type="text", text=f"Sessao criada: {session_id}")],
        structuredContent={"sessionId": session_id},
    )
