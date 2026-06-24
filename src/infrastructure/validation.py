import re

MAX_TERM_LENGTH = 100
MAX_CEP_LENGTH = 9
MIN_PRODUTO_ID = 1
MAX_QUANTIDADE = 999


def sanitize_term(termo: str) -> str:
    cleaned = re.sub(
        r"[^\w\s\-.,áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]", "", termo, flags=re.IGNORECASE
    )
    return cleaned.strip()[:MAX_TERM_LENGTH]


def sanitize_cep(cep: str) -> str:
    cleaned = re.sub(r"[^\d]", "", cep)
    if len(cleaned) != 8:
        return "19700000"
    return cleaned


def validate_produto_id(produto_id: int) -> bool:
    return isinstance(produto_id, int) and produto_id >= MIN_PRODUTO_ID


def validate_quantidade(quantidade: int) -> int:
    if not isinstance(quantidade, int) or quantidade < 1:
        return 1
    return min(quantidade, MAX_QUANTIDADE)


def clamp_limit(limite: int, max_value: int = 100) -> int:
    return min(max(limite, 1), max_value)


def validate_nome_lista(nome: str) -> str:
    cleaned = nome.strip()
    if len(cleaned) > 80:
        cleaned = cleaned[:80]
    return cleaned or "lista"
