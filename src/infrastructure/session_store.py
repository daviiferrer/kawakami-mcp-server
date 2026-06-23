import sqlite3
import time
import uuid
from pathlib import Path
from typing import Optional

from src.config import settings
from src.domain.exceptions import InvalidSessionError
from src.domain.models import CarrinhoItem, ListaCompras

DB_PATH = (
    Path(settings.session_db_path)
    if settings.session_db_path
    else Path(__file__).resolve().parents[2] / "kawakami_sessions.db"
)


class SessionStore:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS cart_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    produto_id INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    preco_unit REAL NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 1,
                    subtotal REAL NOT NULL,
                    un TEXT NOT NULL DEFAULT 'UN',
                    imagem TEXT NOT NULL DEFAULT '',
                    em_oferta INTEGER NOT NULL DEFAULT 0,
                    tag TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS shopping_lists (
                    session_id TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    itens_json TEXT NOT NULL DEFAULT '[]',
                    total REAL NOT NULL DEFAULT 0,
                    criado_em TEXT NOT NULL DEFAULT '',
                    cep TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (session_id, nome),
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
            """)

    def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (id, created_at) VALUES (?, ?)",
                (session_id, time.time()),
            )
        return session_id

    def session_exists(self, session_id: str) -> bool:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        return row is not None

    def require_session(self, session_id: str) -> None:
        if not self.session_exists(session_id):
            raise InvalidSessionError("Sessao invalida ou expirada.")

    def _cleanup_expired(self) -> None:
        ttl = settings.session_ttl_hours * 3600
        cutoff = time.time() - ttl
        with self._get_conn() as conn:
            conn.execute("DELETE FROM sessions WHERE created_at < ?", (cutoff,))

    def add_to_cart(self, sid: str, item: CarrinhoItem) -> list[CarrinhoItem]:
        self.require_session(sid)
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM cart_items WHERE session_id = ? AND produto_id = ?",
                (sid, item.produto_id),
            )
            conn.execute(
                """INSERT INTO cart_items
                   (session_id, produto_id, nome, preco_unit, quantidade,
                    subtotal, un, imagem, em_oferta, tag)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sid,
                    item.produto_id,
                    item.nome,
                    item.preco_unit,
                    item.quantidade,
                    item.subtotal,
                    item.un,
                    item.imagem,
                    int(item.em_oferta),
                    item.tag,
                ),
            )
        return self.get_cart(sid)

    def get_cart(self, sid: str) -> list[CarrinhoItem]:
        self.require_session(sid)
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM cart_items WHERE session_id = ? ORDER BY id", (sid,)
            ).fetchall()
        return [
            CarrinhoItem(
                produto_id=r["produto_id"],
                nome=r["nome"],
                preco_unit=r["preco_unit"],
                quantidade=r["quantidade"],
                subtotal=r["subtotal"],
                un=r["un"],
                imagem=r["imagem"],
                em_oferta=bool(r["em_oferta"]),
                tag=r["tag"],
            )
            for r in rows
        ]

    def remove_from_cart(self, sid: str, termo: str) -> Optional[CarrinhoItem]:
        cart = self.get_cart(sid)
        matches = [i for i in cart if termo.lower() in i.nome.lower()]
        if len(matches) != 1:
            return None
        removed = matches[0]
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM cart_items WHERE session_id = ? AND produto_id = ?",
                (sid, removed.produto_id),
            )
        return removed

    def clear_cart(self, sid: str) -> None:
        self.require_session(sid)
        with self._get_conn() as conn:
            conn.execute("DELETE FROM cart_items WHERE session_id = ?", (sid,))

    def save_list(self, sid: str, nome: str, lista: ListaCompras) -> None:
        self.require_session(sid)
        import json

        itens_json = json.dumps(
            [
                {
                    "produto_id": i.produto_id,
                    "nome": i.nome,
                    "preco_unit": i.preco_unit,
                    "quantidade": i.quantidade,
                    "subtotal": i.subtotal,
                    "un": i.un,
                    "imagem": i.imagem,
                    "em_oferta": i.em_oferta,
                    "tag": i.tag,
                }
                for i in lista.itens
            ]
        )
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO shopping_lists
                   (session_id, nome, itens_json, total, criado_em, cep)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (sid, nome, itens_json, lista.total, lista.criado_em, lista.cep),
            )

    def get_list(self, sid: str, nome: str) -> Optional[ListaCompras]:
        import json

        self.require_session(sid)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM shopping_lists WHERE session_id = ? AND nome = ?",
                (sid, nome),
            ).fetchone()
        if not row:
            return None
        items_data = json.loads(row["itens_json"])
        return ListaCompras(
            nome=row["nome"],
            itens=[CarrinhoItem(**i) for i in items_data],
            total=row["total"],
            criado_em=row["criado_em"],
            cep=row["cep"],
        )

    def get_all_lists(self, sid: str) -> dict[str, ListaCompras]:
        self._cleanup_expired()
        self.require_session(sid)
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM shopping_lists WHERE session_id = ?", (sid,)
            ).fetchall()
        result = {}
        for row in rows:
            lista = self.get_list(sid, row["nome"])
            if lista:
                result[row["nome"]] = lista
        return result

    def delete_list(self, sid: str, nome: str) -> bool:
        self.require_session(sid)
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM shopping_lists WHERE session_id = ? AND nome = ?",
                (sid, nome),
            )
            return cursor.rowcount > 0


session_store = SessionStore()
