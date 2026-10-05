"""Adapter: files in the Obsidian vault and the local state file."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class Vault:
    def __init__(self, root: Path, notes_dir: Path, assets_dir: Path):
        self.root = root
        self.notes_dir = notes_dir
        self.assets_dir = assets_dir

    def write_note(self, title: str, content: str) -> Path:
        """Write a new note; on a name clash append (2), (3), ..."""
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        path = self.notes_dir / f"{title}.md"
        n = 2
        while path.exists():
            path = self.notes_dir / f"{title} ({n}).md"
            n += 1
        path.write_text(content, encoding="utf-8")
        return path

    def append(self, rel_path: str, text: str) -> Optional[Path]:
        path = self.root / rel_path
        if not path.exists():
            return None
        with path.open("a", encoding="utf-8") as f:
            f.write(text)
        return path

    def save_asset(self, name: str, data: bytes) -> str:
        """Save bytes under Assets/Telegram and return the vault-relative path."""
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        path = self.assets_dir / name
        stem, suffix, n = path.stem, path.suffix, 2
        while path.exists():
            path = self.assets_dir / f"{stem}-{n}{suffix}"
            n += 1
        path.write_bytes(data)
        return path.relative_to(self.root).as_posix()

    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()


class State:
    """Last processed update and which Telegram messages already have a note."""

    def __init__(self, path: Path):
        self.path = path
        self.offset: Optional[int] = None
        self.seen: Dict[str, str] = {}      # telegram_id -> vault-relative note path
        self.last_note_path: Optional[str] = None
        self.last_note_ts: Optional[float] = None   # unix time of the last message in the last note
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.offset = data.get("offset")
            self.seen = data.get("seen", {})
            self.last_note_path = data.get("last_note_path")
            self.last_note_ts = data.get("last_note_ts")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"offset": self.offset, "seen": self.seen,
                "last_note_path": self.last_note_path, "last_note_ts": self.last_note_ts}
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
