from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import RAW_DIR


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_raw(source: str, name: str, payload: str | bytes | Any, extension: str = "json") -> Path:
    target_dir = RAW_DIR / source
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{utc_stamp()}_{name}.{extension}"

    if isinstance(payload, bytes):
        path.write_bytes(payload)
    elif isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return path

