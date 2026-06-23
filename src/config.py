from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KWK_", env_file=".env", extra="ignore"
    )

    # VIP Commerce
    vip_base_url: str = "https://services.vipcommerce.com.br/api-admin/v1/org/100"
    vip_org_id: str = "100"
    vip_domain_key: str = "kawakami.com.br"
    vip_token: str = ""
    vip_sessao_id: str = ""
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
    default_cd_id: int = 9

    # Image CDN
    img_base_url: str = "https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250"

    # Session
    session_ttl_hours: int = 24


settings = Settings()
