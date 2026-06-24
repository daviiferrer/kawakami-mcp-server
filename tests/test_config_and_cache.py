import os
from unittest.mock import patch

import pytest

from src.infrastructure.vipcommerce_client import _SearchCache


class TestSettingsValidators:
    def test_port_valid(self):
        with patch.dict(os.environ, {"KWK_PORT": "8080"}, clear=False):
            from src.config import Settings

            s = Settings()
            assert s.port == 8080

    def test_port_invalid_raises(self):
        with patch.dict(os.environ, {"KWK_PORT": "0"}, clear=False):
            from src.config import Settings

            with pytest.raises(ValueError, match="Port must be 1-65535"):
                Settings()

    def test_port_too_high_raises(self):
        with patch.dict(os.environ, {"KWK_PORT": "70000"}, clear=False):
            from src.config import Settings

            with pytest.raises(ValueError, match="Port must be 1-65535"):
                Settings()

    def test_cep_strips_non_digits(self):
        with patch.dict(os.environ, {"KWK_DEFAULT_CEP": "19700-000"}, clear=False):
            from src.config import Settings

            s = Settings()
            assert s.default_cep == "19700000"

    def test_cep_invalid_raises(self):
        with patch.dict(os.environ, {"KWK_DEFAULT_CEP": "123"}, clear=False):
            from src.config import Settings

            with pytest.raises(ValueError, match="CEP must be 8 digits"):
                Settings()

    def test_log_level_uppercased(self):
        with patch.dict(os.environ, {"KWK_LOG_LEVEL": "debug"}, clear=False):
            from src.config import Settings

            s = Settings()
            assert s.log_level == "DEBUG"

    def test_log_level_invalid_raises(self):
        with patch.dict(os.environ, {"KWK_LOG_LEVEL": "TRACE"}, clear=False):
            from src.config import Settings

            with pytest.raises(ValueError, match="log_level must be one of"):
                Settings()


class TestSearchCache:
    def test_set_and_get(self):
        cache = _SearchCache(ttl=300)
        cache.set("key1", ["product1"])
        assert cache.get("key1") == ["product1"]

    def test_returns_none_for_missing_key(self):
        cache = _SearchCache(ttl=300)
        assert cache.get("missing") is None

    def test_expired_entry_returns_none(self):
        cache = _SearchCache(ttl=10)
        cache.set("key1", ["product1"])
        target = "src.infrastructure.vipcommerce_client.time_module.monotonic"
        with patch(target, return_value=cache._data["key1"][1] + 11):
            assert cache.get("key1") is None

    def test_clear(self):
        cache = _SearchCache(ttl=300)
        cache.set("a", [1])
        cache.set("b", [2])
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_overwrite_value(self):
        cache = _SearchCache(ttl=300)
        cache.set("k", [1])
        cache.set("k", [2])
        assert cache.get("k") == [2]


class TestCepToCd:
    def test_paraguacu_paulista(self):
        from src.infrastructure.vipcommerce_client import VipCommerceClient

        assert VipCommerceClient._cep_to_cd("19700000") == 9

    def test_marilia(self):
        from src.infrastructure.vipcommerce_client import VipCommerceClient

        assert VipCommerceClient._cep_to_cd("17522363") == 1

    def test_unknown_cep_returns_default(self):
        from src.infrastructure.vipcommerce_client import VipCommerceClient

        result = VipCommerceClient._cep_to_cd("01000000")
        assert isinstance(result, int)

    def test_strips_non_digits(self):
        from src.infrastructure.vipcommerce_client import VipCommerceClient

        assert VipCommerceClient._cep_to_cd("197-00-000") == 9
