from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KWK_", env_file=".env", extra="ignore")

    # VIP Commerce
    vip_base_url: str = "https://services.vipcommerce.com.br/api-admin/v1/org/100"
    vip_org_id: str = "100"
    vip_domain_key: str = "kawakami.com.br"
    vip_token: str = ""
    vip_sessao_id: str = ""
    vip_fallback_creds: str = ""  # formato: "user1:key1;user2:key2" para refresh do token
    token_file_path: str = ""
    vip_timeout_connect: float = 10.0
    vip_timeout_read: float = 30.0

    # Retry
    retry_max_attempts: int = 3
    retry_backoff_base: float = 1.5

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "ERROR"

    # Defaults
    default_cep: str = "19700000"
    default_cd_id: int = 9  # distribution center: 9=Paraguacu Paulista, 1=Marilia

    # Image CDN
    img_base_url: str = "https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250"
    widget_domain: str = "https://kawakami.axischat.com.br"

    # Session
    session_ttl_hours: int = 24
    session_db_path: str = ""

    # Auth0 OAuth 2.1
    auth0_domain: str = ""
    auth0_audience: str = ""

    def auth0_jwks_url(self) -> str:
        if self.auth0_domain:
            return f"https://{self.auth0_domain}/.well-known/jwks.json"
        return ""

    def auth0_issuer(self) -> str:
        if self.auth0_domain:
            return f"https://{self.auth0_domain}/"
        return ""

    def auth_enabled(self) -> bool:
        return bool(self.auth0_domain)

    @field_validator("port")
    @classmethod
    def port_must_be_valid(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError(f"Port must be 1-65535, got {v}")
        return v

    @field_validator("vip_token")
    @classmethod
    def token_warn_if_empty(cls, v: str) -> str:
        import logging

        cleaned = v.strip()
        if not cleaned:
            logging.getLogger(__name__).warning(
                "KWK_VIP_TOKEN is empty. Auth will fail unless token file exists."
            )
        return cleaned

    @field_validator("default_cep")
    @classmethod
    def cep_must_be_valid(cls, v: str) -> str:
        import re

        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 8:
            raise ValueError(f"CEP must be 8 digits, got '{v}'")
        return cleaned

    @field_validator("log_level")
    @classmethod
    def log_level_valid(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid:
            raise ValueError(f"log_level must be one of {valid}, got '{v}'")
        return v


settings = Settings()
