from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    url_banco_dados: str
    chave_secreta: str
    minutos_expiracao_token: int = 30
    origens_cors: str = "*"
    hosts_permitidos: str = "localhost,127.0.0.1"
    permite_credenciais_cors: bool = False
    supabase_url: str | None = None
    supabase_service_role_key: SecretStr | None = None
    supabase_bucket_anexos: str = "anexos-solicitacoes"

    @property
    def lista_origens_cors(self) -> list[str]:
        return [origem.strip() for origem in self.origens_cors.split(",") if origem.strip()]

    @property
    def lista_hosts_permitidos(self) -> list[str]:
        return [host.strip() for host in self.hosts_permitidos.split(",") if host.strip()]

    @model_validator(mode="after")
    def validar_credenciais_cors(self) -> "Config":
        if self.permite_credenciais_cors and "*" in self.lista_origens_cors:
            raise ValueError(
                "PERMITE_CREDENCIAIS_CORS não pode ser true quando ORIGENS_CORS contém '*'."
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Config()