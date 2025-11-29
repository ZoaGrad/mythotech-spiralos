import os
from pydantic import AnyHttpUrl, BaseSettings, Field, root_validator


class Settings(BaseSettings):
    """Ω.12-B: Canonical configuration spine for SpiralOS.

    Centralizes environment-backed settings with fail-fast validation so
    the system never boots with partial or ambiguous credentials.
    """

    supabase_url: AnyHttpUrl = Field(..., env="SUPABASE_URL")
    supabase_service_role_key: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    environment: str = Field("development", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @root_validator(pre=True)
    def _reject_legacy_keys(cls, values):
        """Prevent drift between anon and service role credentials.

        If a legacy ``SUPABASE_KEY`` is present without the service role key,
        fail immediately rather than allowing partial initialization.
        """

        service_key = values.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY"
        )
        legacy_key = values.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

        if legacy_key and not service_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is required; refusing legacy SUPABASE_KEY"
            )
        return values

    @classmethod
    def load(cls) -> "Settings":
        """Load validated settings from the environment."""

        return cls()

    @property
    def supabase_credentials(self) -> tuple[str, str]:
        """Return a (url, key) tuple ready for the Supabase client."""

        return self.supabase_url, self.supabase_service_role_key
