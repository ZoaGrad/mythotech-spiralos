"""Runtime configuration primitives for SpiralOS."""

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SupabaseSettings(BaseSettings):
    """Configuration for Supabase persistence and RPC access."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="SUPABASE_",
    )

    url: AnyHttpUrl
    anon_key: Optional[str] = None
    service_role_key: Optional[str] = None
    database_schema: str = Field("public", validation_alias="SCHEMA")

    @field_validator("service_role_key", mode="after")
    def ensure_supabase_key(
        cls,
        service_role: Optional[str],
        info: ValidationInfo,
    ) -> Optional[str]:
        """Require at least one credential for Supabase access."""

        anon_key = info.data.get("anon_key")
        if not service_role and not anon_key:
            raise ValueError(
                "Configure SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY before bootstrapping"
            )
        return service_role


class GuardianSettings(BaseSettings):
    """Guardian API authentication, JWT, and rate-limit parameters."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="GUARDIAN_",
    )

    allowed_origins: List[str] = Field(
        default_factory=lambda: ["https://spiralos.io", "https://guardian.spiralos.io"],
    )
    api_keys: List[str]
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: Optional[str] = None
    jwt_audience: Optional[str] = None
    rate_limit_per_minute: int = 10
    rate_window_seconds: int = 60

    @field_validator("allowed_origins", "api_keys", mode="before")
    def split_comma_separated(
        cls,
        value,
    ):  # type: ignore[override]
        """Allow comma-delimited configuration entries."""

        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


class VaultNodeSettings(BaseSettings):
    """VaultNode identifier defaults for bridge operations."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        env_prefix="VAULTNODE_",
    )

    default_id: str = "ΔΩ.122.0"


@lru_cache()
def get_supabase_settings() -> SupabaseSettings:
    """Load Supabase settings once per process."""

    return SupabaseSettings()


@lru_cache()
def get_guardian_settings() -> GuardianSettings:
    """Load Guardian authentication and rate-limit settings."""

    return GuardianSettings()


@lru_cache()
def get_vaultnode_settings() -> VaultNodeSettings:
    """Load VaultNode defaults."""

    return VaultNodeSettings()


def reset_settings_cache() -> None:
    """Clear cached BaseSettings instances (used by tests)."""

    get_guardian_settings.cache_clear()
    get_supabase_settings.cache_clear()
    get_vaultnode_settings.cache_clear()


__all__ = [
    "GuardianSettings",
    "SupabaseSettings",
    "VaultNodeSettings",
    "get_guardian_settings",
    "get_supabase_settings",
    "get_vaultnode_settings",
    "reset_settings_cache",
]
