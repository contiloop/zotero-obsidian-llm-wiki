#!/usr/bin/env python3
"""Entry point. Run from anywhere:  python3 System/Telegram/ingest.py [--dry-run] [--whoami]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from telegram_ingest.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
