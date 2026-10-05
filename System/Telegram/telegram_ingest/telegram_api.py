"""Adapter: Telegram Bot API over HTTPS with the standard library only."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

API = "https://api.telegram.org"
BOT_FILE_LIMIT = 20 * 1024 * 1024   # Bot API refuses getFile above 20 MB


class TelegramError(RuntimeError):
    pass


class BotApi:
    def __init__(self, token: str, timeout: int = 60):
        self.token = token
        self.timeout = timeout

    def _call(self, method: str, **params) -> dict:
        url = f"{API}/bot{self.token}/{method}"
        data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
        try:
            with urllib.request.urlopen(url, data=data, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                payload = json.loads(e.read().decode("utf-8"))
            except Exception:
                raise TelegramError(f"{method}: HTTP {e.code}") from e
            raise TelegramError(f"{method}: {payload.get('description', e)}") from e
        except urllib.error.URLError as e:
            raise TelegramError(f"{method}: network error: {e.reason}") from e
        if not payload.get("ok"):
            raise TelegramError(f"{method}: {payload.get('description')}")
        return payload["result"]

    def get_me(self) -> dict:
        return self._call("getMe")

    def get_updates(self, offset: Optional[int]) -> List[dict]:
        """All pending updates. Telegram keeps undelivered updates for 24 hours only."""
        results: List[dict] = []
        while True:
            batch = self._call("getUpdates", offset=offset, limit=100, timeout=0,
                               allowed_updates=json.dumps(["message"]))
            results.extend(batch)
            if len(batch) < 100:
                return results
            offset = batch[-1]["update_id"] + 1

    def download(self, file_id: str) -> bytes:
        info = self._call("getFile", file_id=file_id)
        path = info.get("file_path")
        if not path:
            raise TelegramError("getFile returned no file_path (file too large for a bot?)")
        url = f"{API}/file/bot{self.token}/{path}"
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            return resp.read()
