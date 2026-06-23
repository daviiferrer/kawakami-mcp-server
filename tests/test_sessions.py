import re

import pytest

from src.infrastructure.session_store import SessionStore


def test_create_session_persists_opaque_identifier(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")

    session_id = store.create_session()

    assert re.fullmatch(r"[0-9a-f]{32}", session_id)
    assert store.session_exists(session_id)


def test_require_session_rejects_unknown_identifier(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")

    with pytest.raises(ValueError, match="Sessao invalida"):
        store.require_session("0" * 32)


def test_create_session_generates_distinct_identifiers(tmp_path):
    store = SessionStore(tmp_path / "sessions.db")

    first = store.create_session()
    second = store.create_session()

    assert first != second
