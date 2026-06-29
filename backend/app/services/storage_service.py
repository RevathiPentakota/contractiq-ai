"""Storage service – Supabase file operations.

Handles downloading files from Supabase Storage for contract processing.
Abstracts away Supabase SDK details so DocumentAgent remains thin and
easily testable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.logging import logger

if TYPE_CHECKING:
    from pathlib import Path


class StorageService:
    """Service for downloading files from Supabase Storage.

    Attributes:
        bucket_name: Name of the Supabase Storage bucket (e.g. "contracts").
        client: Supabase client instance (lazy-loaded).
    """

    def __init__(self, bucket_name: str = "contracts") -> None:
        self.bucket_name = bucket_name
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Lazy-load and cache the Supabase client."""
        if self._client is None:
            settings = get_settings()
            if not settings.supabase_url or not settings.supabase_anon_key:
                raise ValueError(
                    "Supabase credentials not configured. "
                    "Set SUPABASE_URL and SUPABASE_ANON_KEY."
                )
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key,
            )
        return self._client

    def download_file(self, storage_path: str) -> bytes:
        """Download a file from Supabase Storage.

        Args:
            storage_path: Relative path within the bucket
                         (e.g. "2024/contract_123.pdf").

        Returns:
            Raw file bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: On network or API errors.

        Example:
            >>> service = StorageService("contracts")
            >>> data = await service.download_file("2024/sample.pdf")
            >>> len(data)  # file size in bytes
        """
        logger.debug(
            "[StorageService] Downloading file: {path}",
            path=storage_path,
        )

        try:
            response = self.client.storage.from_(self.bucket_name).download(
                storage_path
            )
            return response
        except Exception as err:
            logger.error(
                "[StorageService] Failed to download {path}: {error}",
                path=storage_path,
                error=str(err),
            )
            raise
