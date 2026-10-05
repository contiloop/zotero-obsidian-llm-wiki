"""Command line: python3 System/Telegram/ingest.py [--dry-run] [--whoami]"""
from __future__ import annotations

import argparse
import sys

from .config import load_config
from .service import run
from .telegram_api import BotApi, TelegramError
from .vault import State, Vault


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch messages forwarded to the bot and write source notes.")
    parser.add_argument("--dry-run", action="store_true", help="show what would be written, change nothing")
    parser.add_argument("--whoami", action="store_true", help="check the token and print the bot name")
    args = parser.parse_args(argv)

    cfg = load_config()
    api = BotApi(cfg.bot_token)
    try:
        if args.whoami:
            me = api.get_me()
            print(f"Bot: @{me.get('username')} (id {me.get('id')}). Forward messages to this bot.")
            return 0
        vault = Vault(cfg.vault_root, cfg.notes_dir, cfg.assets_dir)
        state = State(cfg.state_file)
        res = run(cfg, api, vault, state, dry_run=args.dry_run)
    except TelegramError as e:
        print(f"Telegram error: {e}", file=sys.stderr)
        return 1

    for p in res.created:
        print(f"created   {p}")
    for p in res.commented:
        print(f"comment   {p}")
    for w in res.warnings:
        print(f"warning   {w}")
    if res.rejected_senders:
        print(f"ignored messages from user id(s) {res.rejected_senders} "
              f"(not in TELEGRAM_ALLOWED_USER_IDS)")
    if not res.created and not res.commented:
        print("nothing new")
    return 0


if __name__ == "__main__":
    sys.exit(main())
