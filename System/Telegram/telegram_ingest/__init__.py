"""Turn messages forwarded to a private Telegram bot into source notes in References/Telegram/.

Layout (ports and adapters):
- domain.py        pure logic: Bot API message -> Capture -> Note (no network, no disk)
- telegram_api.py  adapter: Telegram Bot API over HTTPS
- vault.py         adapter: files in the Obsidian vault and the local state file
- service.py       core use case wiring the two adapters through small interfaces
- config.py        settings from .env / environment
"""
