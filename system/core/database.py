from __future__ import annotations

from typing import Optional

from supabase import Client, create_client

from system.core.config.settings import Settings


class SupabaseManager:
    """Ω.12-B: Hardened Supabase client lifecycle management."""

    _settings: Optional[Settings] = None
    _client: Optional[Client] = None

    @classmethod
    def settings(cls) -> Settings:
        if cls._settings is None:
            cls._settings = Settings.load()
        return cls._settings

    @classmethod
    def get_client(cls) -> Client:
        """Return a cached Supabase client bound to the service role key."""

        if cls._client is None:
            url, key = cls.settings().supabase_credentials
            cls._client = create_client(str(url), key)
        return cls._client

    @classmethod
    def verify_connection(cls) -> None:
        """Fail fast if Supabase credentials are missing or unusable."""

        settings = cls.settings()

        if not settings.supabase_service_role_key:
            raise RuntimeError("Supabase service role key is not configured")
        if not settings.supabase_url:
            raise RuntimeError("Supabase URL is not configured")

        client = cls.get_client()
        try:
            # Storage bucket listing is safe and does not depend on app tables.
            client.storage.list_buckets()
        except Exception as exc:  # pragma: no cover - dependency failure path
            raise RuntimeError("Supabase connectivity check failed") from exc
