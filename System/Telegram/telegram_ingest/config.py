"""Settings. Read from System/Telegram/.env, then from the process environment (environment wins)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

HERE = Path(__file__).resolve().parent          # System/Telegram/telegram_ingest
VAULT_ROOT = HERE.parents[2]                    # vault root
ENV_FILE = HERE.parent / ".env"


@dataclass
class Config:
    bot_token: str
    vault_root: Path = VAULT_ROOT
    notes_dir: Path = VAULT_ROOT / "References" / "Telegram"
    assets_dir: Path = VAULT_ROOT / "Assets" / "Telegram"
    state_file: Path = VAULT_ROOT / "System" / ".cache" / "telegram" / "state.json"
    allowed_user_ids: List[int] = field(default_factory=list)
    comment_window_seconds: int = 180


def _read_env_file(path: Path) -> dict:
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(env_file: Optional[Path] = None) -> Config:
    values = _read_env_file(env_file or ENV_FILE)
    values.update({k: v for k, v in os.environ.items() if k.startswith("TELEGRAM_")})

    token = values.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit(
            f"TELEGRAM_BOT_TOKEN is not set. Copy {ENV_FILE.parent / '.env.example'} to {ENV_FILE} "
            "and paste the token from @BotFather."
        )

    ids_raw = values.get("TELEGRAM_ALLOWED_USER_IDS", "")
    allowed = [int(x) for x in ids_raw.replace(";", ",").split(",") if x.strip()]

    window = int(values.get("TELEGRAM_COMMENT_WINDOW_SECONDS", "180"))
    return Config(bot_token=token, allowed_user_ids=allowed, comment_window_seconds=window)
