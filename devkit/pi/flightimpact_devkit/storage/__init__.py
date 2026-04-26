"""Shot storage — SQLite via aiosqlite.

Shots are stored as a single JSON blob per row plus indexed columns for
captured_at and session_id for fast querying. Keeps the schema flexible while
metrics evolve.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiosqlite

from core.models import Shot

logger = logging.getLogger(__name__)


SCHEMA = """
CREATE TABLE IF NOT EXISTS shots (
    id          TEXT PRIMARY KEY,
    captured_at TEXT NOT NULL,
    session_id  TEXT,
    status      TEXT NOT NULL,
    payload     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_shots_captured_at ON shots (captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_shots_session ON shots (session_id);
"""


class Storage:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def open(self) -> None:
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(SCHEMA)
        await self._db.commit()
        logger.info("Storage opened at %s", self._db_path)

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def save_shot(self, shot: Shot) -> None:
        assert self._db is not None
        await self._db.execute(
            """
            INSERT INTO shots (id, captured_at, session_id, status, payload)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                captured_at = excluded.captured_at,
                session_id = excluded.session_id,
                status = excluded.status,
                payload = excluded.payload
            """,
            (
                str(shot.id),
                shot.captured_at.isoformat(),
                str(shot.session_id) if shot.session_id else None,
                shot.status.value,
                shot.model_dump_json(),
            ),
        )
        await self._db.commit()

    async def get_shot(self, shot_id: UUID) -> Optional[Shot]:
        assert self._db is not None
        async with self._db.execute(
            "SELECT payload FROM shots WHERE id = ?", (str(shot_id),)
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return None
        return Shot.model_validate_json(row[0])

    async def list_shots(self, limit: int = 50, offset: int = 0) -> list[Shot]:
        assert self._db is not None
        async with self._db.execute(
            "SELECT payload FROM shots ORDER BY captured_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
        return [Shot.model_validate_json(r[0]) for r in rows]

    async def delete_shot(self, shot_id: UUID) -> bool:
        assert self._db is not None
        cursor = await self._db.execute(
            "DELETE FROM shots WHERE id = ?", (str(shot_id),)
        )
        await self._db.commit()
        return cursor.rowcount > 0
