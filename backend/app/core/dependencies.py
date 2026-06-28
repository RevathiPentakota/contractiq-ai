"""FastAPI dependency providers.

Use these with ``Depends()`` across route handlers to inject shared
resources (database sessions, settings, etc.).
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session

# ── Settings ───────────────────────────────────────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]

# ── Database session ───────────────────────────────────────────────────────────

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
