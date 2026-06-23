import json
import logging
import os

import httpx

from src.config import settings
from src.domain.exceptions import TokenExpiredError

logger = logging.getLogger(__name__)

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".kawakami_token.json")

FALLBACK_CREDENTIALS: list[dict[str, str]] = []
_raw = settings.vip_fallback_creds.strip() if hasattr(settings, "vip_fallback_creds") else ""
if _raw:
    for pair in _raw.split(";"):
        parts = pair.split(":", 1)
        if len(parts) == 2:
            FALLBACK_CREDENTIALS.append({"username": parts[0].strip(), "key": parts[1].strip()})
if not FALLBACK_CREDENTIALS:
    FALLBACK_CREDENTIALS = [
        {"username": "guest", "key": "kawakami"},
    ]


class TokenManager:
    def __init__(self) -> None:
        self._token: str = ""
        self._sessao_id: str = ""

    def load(self) -> None:
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE) as f:
                    data = json.load(f)
                self._token = data.get("token", "")
                self._sessao_id = data.get("sessao_id", "")
            except Exception:
                pass
        if not self._token:
            self._token = settings.vip_token
            self._sessao_id = settings.vip_sessao_id

    def save(self) -> None:
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump({"token": self._token, "sessao_id": self._sessao_id}, f)
        except Exception:
            pass

    async def refresh(self) -> bool:
        timeout = httpx.Timeout(settings.vip_timeout_connect, read=settings.vip_timeout_read)
        async with httpx.AsyncClient(timeout=timeout) as c:
            for i, body in enumerate(FALLBACK_CREDENTIALS):
                try:
                    r = await c.post(
                        f"{settings.vip_base_url}/auth/loja/login",
                        json=body,
                        headers={
                            "organizationid": settings.vip_org_id,
                            "domainkey": settings.vip_domain_key,
                            "content-type": "application/json",
                            "referer": "https://www.kawakami.com.br/",
                            "origin": "https://www.kawakami.com.br",
                        },
                    )
                    if r.status_code == 200:
                        data = r.json()
                        d = data.get("data", data) if isinstance(data, dict) else {}
                        if isinstance(d, dict):
                            token = d.get("token") or d.get("access_token")
                            sessao = d.get("sessao_id") or d.get("session_id") or d.get("id")
                            if token:
                                self._token = token
                                self._sessao_id = sessao or ""
                                self.save()
                                logger.info("Token refreshed via credential %d", i + 1)
                                return True
                except Exception as e:
                    logger.debug("Credential %d failed: %s", i + 1, str(e)[:80])
                    continue
        logger.error("All %d fallback credentials failed", len(FALLBACK_CREDENTIALS))
        return False

    @property
    def headers(self) -> dict:
        if not self._token:
            self.load()
        return {
            "authorization": f"Bearer {self._token}",
            "sessao-id": self._sessao_id,
            "organizationid": settings.vip_org_id,
            "domainkey": settings.vip_domain_key,
        }


token_manager = TokenManager()
