from src.infrastructure.validation import (
    validate_nome_lista,
    validate_produto_id,
    validate_quantidade,
)


class TestValidateProdutoId:
    def test_valid_id(self):
        assert validate_produto_id(1) is True
        assert validate_produto_id(999) is True

    def test_zero_is_invalid(self):
        assert validate_produto_id(0) is False

    def test_negative_is_invalid(self):
        assert validate_produto_id(-1) is False


class TestValidateQuantidade:
    def test_valid(self):
        assert validate_quantidade(1) == 1
        assert validate_quantidade(100) == 100

    def test_zero_returns_one(self):
        assert validate_quantidade(0) == 1

    def test_negative_returns_one(self):
        assert validate_quantidade(-5) == 1

    def test_above_max_clamped(self):
        assert validate_quantidade(1000) == 999
        assert validate_quantidade(9999) == 999


class TestValidateNomeLista:
    def test_normal_name(self):
        assert validate_nome_lista("Compras da Semana") == "Compras da Semana"

    def test_strips_whitespace(self):
        assert validate_nome_lista("  padaria  ") == "padaria"

    def test_truncates_long_name(self):
        long_name = "x" * 100
        assert len(validate_nome_lista(long_name)) == 80

    def test_empty_returns_default(self):
        assert validate_nome_lista("") == "lista"

    def test_whitespace_only_returns_default(self):
        assert validate_nome_lista("   ") == "lista"
