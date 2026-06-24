from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Oferta:
    oferta_id: int
    nome: str
    tag: str
    preco_oferta: float
    preco_antigo: float
    quantidade_minima: int = 1
    quantidade_maxima: int = 6

    @property
    def desconto_pct(self) -> float:
        if self.preco_antigo > 0:
            return round((1 - self.preco_oferta / self.preco_antigo) * 100)
        return 0.0


@dataclass
class Produto:
    produto_id: int
    descricao: str
    preco: float
    unidade_sigla: str
    imagem: str
    disponivel: bool
    quantidade_maxima: int
    codigo_barras: str = ""
    sku: str = ""
    codigo_erp: str = ""
    quantidade_vendida: int = 0
    link: str = ""
    secao_id: int = 0
    dept_name: str = ""
    em_oferta: bool = False
    oferta: Optional[Oferta] = None

    @property
    def preco_efetivo(self) -> float:
        if self.em_oferta and self.oferta:
            return self.oferta.preco_oferta
        return self.preco

    @classmethod
    def from_api(cls, data: dict) -> "Produto":
        oferta = None
        if data.get("em_oferta") and data.get("oferta"):
            o = data["oferta"]
            oferta = Oferta(
                oferta_id=o.get("oferta_id", 0),
                nome=o.get("nome", ""),
                tag=o.get("tag", ""),
                preco_oferta=float(o.get("preco_oferta", 0)),
                preco_antigo=float(o.get("preco_antigo", 0)),
                quantidade_minima=o.get("quantidade_minima", 1),
                quantidade_maxima=o.get("quantidade_maxima", 6),
            )
        return cls(
            produto_id=data.get("produto_id", 0),
            descricao=data.get("descricao", ""),
            preco=float(data.get("preco", 0)),
            unidade_sigla=data.get("unidade_sigla", "UN"),
            imagem=data.get("imagem", ""),
            disponivel=data.get("disponivel", False),
            quantidade_maxima=int(data.get("quantidade_maxima", 0)),
            codigo_barras=data.get("codigo_barras", ""),
            sku=data.get("sku", ""),
            codigo_erp=str(data.get("codigo_erp", "")),
            quantidade_vendida=int(data.get("quantidade_vendida", 0)),
            link=data.get("link", ""),
            secao_id=data.get("secao_id", 0),
            em_oferta=data.get("em_oferta", False),
            oferta=oferta,
        )


@dataclass
class CarrinhoItem:
    produto_id: int
    nome: str
    preco_unit: float
    quantidade: int
    subtotal: float
    un: str
    imagem: str
    em_oferta: bool = False
    tag: str = ""

    @classmethod
    def from_produto(cls, produto: "Produto", quantidade: int = 1) -> "CarrinhoItem":
        price = produto.preco_efetivo
        tag = produto.oferta.tag if produto.oferta else ""
        return cls(
            produto_id=produto.produto_id,
            nome=produto.descricao,
            preco_unit=price,
            quantidade=quantidade,
            subtotal=round(price * quantidade, 2),
            un=produto.unidade_sigla,
            imagem=produto.imagem,
            em_oferta=produto.em_oferta,
            tag=tag,
        )

    @staticmethod
    def total(items: "list[CarrinhoItem]") -> float:
        return sum(item.subtotal for item in items)


@dataclass
class ListaCompras:
    nome: str
    itens: list[CarrinhoItem] = field(default_factory=list)
    total: float = 0.0
    criado_em: str = ""
    cep: str = ""


@dataclass
class Departamento:
    id: int
    nome: str
    total_ofertas: int = 0
    total_produtos: int = 0
