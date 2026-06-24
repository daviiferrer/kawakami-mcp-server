import asyncio
import logging
import time as time_module
from typing import Optional
from urllib.parse import quote

import httpx

from src.config import settings
from src.domain.exceptions import TokenExpiredError, VipCommerceUnavailableError
from src.domain.models import Departamento, Produto
from src.infrastructure.auth import token_manager
from src.infrastructure.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class _SearchCache:
    def __init__(self, ttl: float = 300) -> None:
        self._data: dict[str, tuple[list[Produto], float]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[list[Produto]]:
        if key in self._data:
            produtos, ts = self._data[key]
            if time_module.monotonic() - ts < self._ttl:
                return produtos
            del self._data[key]
        return None

    def set(self, key: str, produtos: list[Produto]) -> None:
        self._data[key] = (produtos, time_module.monotonic())

    def clear(self) -> None:
        self._data.clear()


class VipCommerceClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.vip_timeout_connect, read=settings.vip_timeout_read),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        )
        self._dept_cache: Optional[list[Departamento]] = None
        self._dept_cache_ts: float = 0.0
        self._dept_cache_key: str = ""
        self._search_cache = _SearchCache(ttl=300)
        self._breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

    def _build_url(self, path: str, cep: str = "") -> str:
        cd_id = self._cep_to_cd(cep) if cep else settings.default_cd_id
        return f"{settings.vip_base_url}/filial/1/centro_distribuicao/{cd_id}/loja{path}"

    @staticmethod
    def _cep_to_cd(cep: str) -> int:
        cep_clean = "".join(c for c in cep if c.isdigit())
        cep_map = {
            "19700000": 9,  # Paraguacu Paulista
            "17522363": 1,  # Marilia
        }
        return cep_map.get(cep_clean, settings.default_cd_id)

    async def _request(
        self, url: str, params: Optional[dict] = None, retries: int | None = None
    ) -> httpx.Response:
        if not self._breaker.allow_request():
            raise VipCommerceUnavailableError(
                "VIP Commerce temporariamente indisponivel. Tente novamente em breve."
            )

        max_retries = retries if retries is not None else settings.retry_max_attempts
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = await self._client.get(
                    url,
                    params=params,
                    headers=token_manager.headers,
                )
                if resp.status_code == 401:
                    refreshed = await token_manager.refresh()
                    if refreshed and attempt < max_retries - 1:
                        continue
                    raise TokenExpiredError("Token refresh failed")
                if resp.status_code in (502, 503, 504):
                    raise VipCommerceUnavailableError(f"VIP Commerce returned {resp.status_code}")
                resp.raise_for_status()
                self._breaker.record_success()
                logger.debug("VIP request OK: %s", url)
                return resp
            except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError) as e:
                last_error = e
                logger.warning("VIP request attempt %d failed: %s", attempt + 1, str(e)[:100])
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.retry_backoff_base**attempt)
            except VipCommerceUnavailableError as e:
                last_error = e
                logger.warning("VIP unavailable (attempt %d): %s", attempt + 1, str(e))
                if attempt < max_retries - 1:
                    await asyncio.sleep(settings.retry_backoff_base**attempt)

        self._breaker.record_failure()
        raise last_error or VipCommerceUnavailableError("Max retries exceeded")

    async def search_products(
        self, termo: str, page: int = 1, cep: str = ""
    ) -> tuple[list[Produto], dict]:
        if page == 1:
            cache_key = f"search:{termo.lower()}:{cep}"
            cached = self._search_cache.get(cache_key)
            if cached:
                return cached, {"total_items": len(cached), "page": 1, "total_pages": 1}

        url = self._build_url(f"/buscas/produtos/termo/{quote(termo, safe='')}", cep)
        resp = await self._request(url, params={"page": page})
        data = resp.json()
        produtos_raw = data.get("data", {}).get("produtos", data.get("data", []))
        produtos = [Produto.from_api(p) for p in produtos_raw]
        paginator = data.get("paginator", {})

        if page == 1 and produtos:
            self._search_cache.set(f"search:{termo.lower()}:{cep}", produtos)

        return produtos, paginator

    async def get_departments(self, cep: str = "") -> list[Departamento]:
        now = time_module.monotonic()
        cache_key = f"depts:{cep}"
        if (
            hasattr(self, "_dept_cache_key")
            and self._dept_cache_key == cache_key
            and self._dept_cache
            and (now - self._dept_cache_ts) < 3600
        ):
            return self._dept_cache

        url = self._build_url("/classificacoes_mercadologicas/departamentos/arvore", cep)
        resp = await self._request(url)
        data = resp.json()
        depts = []
        if data.get("success") and data.get("data"):
            for d in data["data"]:
                depts.append(
                    Departamento(
                        id=d.get("classificacao_mercadologica_id", 0),
                        nome=d.get("descricao", ""),
                        total_ofertas=d.get("total_ofertas", 0),
                        total_produtos=d.get("total_produtos", 0),
                    )
                )
        self._dept_cache = depts
        self._dept_cache_ts = now
        self._dept_cache_key = cache_key
        return depts

    async def get_products_by_department(
        self,
        dept_id: int,
        limit: int = 500,
        only_offers: bool = False,
        cep: str = "",
    ) -> tuple[list[Produto], dict]:
        url = self._build_url(
            f"/classificacoes_mercadologicas/departamentos/{dept_id}/produtos",
            cep,
        )
        page = 1
        page_size = min(max(limit, 1), 500)
        max_pages = 5 if only_offers else 1000
        produtos: list[Produto] = []
        paginator: dict = {}

        while True:
            resp = await self._request(
                url,
                params={"page": page, "limit": page_size},
            )
            data = resp.json()
            page_products = [Produto.from_api(p) for p in data.get("data", [])]
            produtos.extend(page_products)
            paginator = data.get("paginator", {})
            total_pages = int(paginator.get("total_pages", page))

            if page >= total_pages or not page_products or page >= max_pages:
                break
            if only_offers:
                if len([p for p in produtos if p.em_oferta]) >= limit:
                    break
            elif len(produtos) >= limit:
                break
            page += 1

        if only_offers:
            produtos = [p for p in produtos if p.em_oferta]
        return produtos[:limit], paginator

    async def get_product_by_id(self, produto_id: int, cep: str = "") -> Optional[Produto]:
        produtos, _ = await self.search_products(str(produto_id), page=1, cep=cep)
        for product in produtos:
            if product.produto_id == produto_id:
                return product

        depts = await self.get_departments(cep=cep)
        tasks = [self.get_products_by_department(dept.id, limit=100_000, cep=cep) for dept in depts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(
                    "Department %s failed during product lookup: %s",
                    depts[idx].id,
                    type(result).__name__,
                )
                continue
            produtos, _ = result
            dept_name = depts[idx].nome if idx < len(depts) else ""
            for p in produtos:
                if p.produto_id == produto_id:
                    p.dept_name = dept_name
                    return p
        return None

    async def get_best_offers(self, limit: int = 50, cep: str = "") -> list[Produto]:
        cache_key = f"offers:{cep}:{limit}"
        cached = self._search_cache.get(cache_key)
        if cached:
            return cached

        depts = await self.get_departments(cep=cep)
        tasks = [
            self.get_products_by_department(
                dept.id,
                limit=limit,
                only_offers=True,
                cep=cep,
            )
            for dept in depts
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_offers: list[Produto] = []
        successful_departments = 0
        first_error: Exception | None = None
        for dept, result in zip(depts, results):
            if isinstance(result, Exception):
                first_error = first_error or result
                logger.warning(
                    "Department %s failed during offers lookup: %s",
                    dept.id,
                    type(result).__name__,
                )
                continue
            successful_departments += 1
            produtos, _ = result
            all_offers.extend(p for p in produtos if p.em_oferta)

        if depts and successful_departments == 0:
            if isinstance(first_error, VipCommerceUnavailableError):
                raise first_error
            raise VipCommerceUnavailableError("Falha ao consultar todos os departamentos.")

        all_offers.sort(key=lambda p: p.oferta.desconto_pct if p.oferta else 0, reverse=True)
        result = all_offers[:limit]
        self._search_cache.set(cache_key, result)
        return result

    def clear_cache(self) -> None:
        self._dept_cache = None
        self._dept_cache_ts = 0.0
        self._search_cache.clear()

    async def close(self) -> None:
        await self._client.aclose()


vip_client = VipCommerceClient()
