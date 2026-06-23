import json
import os
import httpx
from src.config import settings
from src.domain.exceptions import TokenExpiredError

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".kawakami_token.json")


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
            for body in [
                {"username": "guest", "key": "kawakami"},
                {"username": "kawakami.com.br", "key": "vipcommerce"},
                {"username": "100", "key": "kawakami"},
            ]:
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
                                return True
                except Exception:
                    continue
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
