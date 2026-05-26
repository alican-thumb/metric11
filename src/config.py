from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

SEASON = "2025_2026"
SEASON_LABEL = "2025-2026"

# Current transfer-window monitoring is newer than the completed analytical season.
# Keep its snapshots separate so network refreshes cannot overwrite model inputs.
TRANSFER_WATCH_SEASON = "2026_2027"
TRANSFER_WATCH_SEASON_LABEL = "2026-2027"


@dataclass(frozen=True)
class Settings:
    api_football_key: str | None
    football_data_key: str | None
    x_bearer_token: str | None
    tff_sample_match_ids: list[str]


def load_settings() -> Settings:
    env_path = ROOT_DIR / ".env"
    if load_dotenv and env_path.exists():
        load_dotenv(env_path)
    elif load_dotenv and (ROOT_DIR / ".env.example").exists():
        load_dotenv(ROOT_DIR / ".env.example")

    match_ids = os.getenv("TFF_SAMPLE_MATCH_IDS", "249505,249392,264125,264089")
    return Settings(
        api_football_key=os.getenv("API_FOOTBALL_KEY") or None,
        football_data_key=os.getenv("FOOTBALL_DATA_KEY") or None,
        x_bearer_token=os.getenv("X_BEARER_TOKEN") or None,
        tff_sample_match_ids=[item.strip() for item in match_ids.split(",") if item.strip()],
    )


def ensure_data_dirs() -> None:
    for path in (RAW_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)
