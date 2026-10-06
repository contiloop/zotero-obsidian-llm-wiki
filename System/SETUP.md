---
type: system
---

# Setup

How to rebuild this vault's setup on a new machine (or after reinstalling). This repository contains the setup only: structure, AI rules, templates and settings. Content stays local.

## 1. Quick path

```bash
git clone https://github.com/contiloop/zotero-obsidian-llm-wiki.git
cd zotero-obsidian-llm-wiki
System/setup.sh
```

The script is safe to run again at any time. It checks the tools (git, python3, curl), downloads the ZotLit plugin files for the pinned version, marks the two local-only files so their changes stay out of git, creates `System/Telegram/.env` and asks for the bot token and your Telegram user id, installs the 6-hourly fetch job, and ends with a check and a list of what is still to do by hand. Subcommands: `base`, `telegram`, `schedule`, `unschedule`, `check`.

What only a person can do, in order:

1. **Obsidian**: File → Open folder as vault → the cloned folder. Settings → Community plugins → turn off Restricted mode (ZotLit is already enabled in the stored settings). If your Zotero data folder is not `~/Zotero`, set it in Settings → ZotLit.
2. **Zotero**: install Better BibTeX and ZotLit Companion (section 4), and the browser connector.
3. **Telegram**: create a bot with @BotFather (`/newbot`), paste the token when the script asks or into `System/Telegram/.env`, open the bot chat and press Start.
4. **macOS permission** (only if the vault is inside `~/Documents`, `~/Desktop` or `~/Downloads`): allow Full Disk Access for the Python app the schedule uses (section 6). Then run `System/setup.sh schedule` again.

Finish with `System/setup.sh check`; every line should be a ✓. The sections below are the reference for each piece, for troubleshooting or for an AI assistant doing the setup.

## 2. Apps

| App | Version tested | Notes |
| --- | --- | --- |
| Obsidian | 1.13.7 | ZotLit needs Obsidian installer 1.13.4+ |
| Zotero | 10.0.5 | |
| Better BibTeX (Zotero plugin) | 9.0.63 | Generates citekeys |
| ZotLit Companion (Zotero plugin) | 2.1.4 | `zotlit-zotero-2.1.4.xpi` |
| ZotLit (Obsidian plugin) | 2.1.4 | Files downloaded by `System/setup.sh base` |
| Python | 3.9+ (macOS command line tools or Homebrew) | Standard library only |

## 3. ZotLit (Obsidian plugin)

Plugin code is not stored in this repository. Settings are (`.obsidian/plugins/zotlit/data.json`, `manifest.json`).

1. `System/setup.sh base` downloads `main.js` and `styles.css` for version 2.1.4 into `.obsidian/plugins/zotlit/` (by hand: https://github.com/aidenlx/zotlit/releases)
2. Obsidian → Settings → Community plugins → turn off Restricted mode; **ZotLit** is listed as enabled
3. Settings → ZotLit → Zotero database: point it to your Zotero data folder (default `~/Zotero`)
4. Settings → ZotLit → Templates → **Frontmatter**: confirm the fields below exist. If they are missing, add them with the **+** button (Language: Liquid, Merge: Replace).

| Key | Expression |
| --- | --- |
| captured | `zt.dateAdded \| date: "%Y-%m-%d"` |
| published | `zt.date \| date: "%Y-%m-%d"` |
| url | `zt.url` |

Settings already stored in this repository: literature note folder `References/Zotero`, template folder `System/ZotLit` (color-grouped highlights, title-based file names), attachment folder `Assets/Zotero` (images from area highlights).

## 4. Zotero

1. Install Better BibTeX and ZotLit Companion: Zotero → Tools → Plugins → **Install Plugin From File** (ZotLit Companion: https://github.com/aidenlx/zotlit/releases).
2. Install the Zotero Connector for your browser.
3. Optional: turn on Zotero sync (zotero.org account) so saved items, snapshots and highlights survive a machine change.
4. Create a standalone note at the top of My Library titled `00 색상 규칙` with the legend below.

| Color | Meaning |
| --- | --- |
| Yellow | Key claims |
| Red | Data & figures |
| Green | For my writing |
| Blue | Definitions & concepts |
| Purple | Counterpoints & questions |
| Orange | Outlook & forecasts |

## 5. Check that it works

1. Save a web page with the Zotero Connector.
2. Open the snapshot in Zotero, highlight a few sentences in different colors, add a comment to one.
3. Keep Obsidian open. In Zotero, right-click the item → **ZotLit → Create or Update Literature Note**.
4. A note named after the item title should appear in `References/Zotero/` with `captured`, `url` and highlights grouped by color.

A PDF dropped into Zotero directly (from Telegram, a download folder, etc.) becomes a standalone attachment, and ZotLit shows no menu for it. Right-click the PDF → **Create Parent Item…** → Manual Entry (type Report, fill in title, date, institution). The ZotLit menu then appears on the parent; existing highlights stay on the PDF.

## 6. Telegram (optional)

Forwarded Telegram messages become source notes in `References/Telegram/`. The script needs only Python 3 (standard library). `System/setup.sh telegram` does steps 2 and 4 and asks for the values.

1. In Telegram, open **@BotFather** → `/newbot` → pick a name and a username. Copy the token.
2. Copy `System/Telegram/.env.example` to `System/Telegram/.env` and paste the token. `.env` is gitignored.
3. Open the chat with your new bot and press **Start**.
4. Check the token:

```bash
python3 System/Telegram/ingest.py --whoami
```

5. Forward a message (or an album) to the bot. If you want to add your own comment, send a plain text message right after it (within 3 minutes) or reply to the forwarded message.
6. Run the ingest:

```bash
python3 System/Telegram/ingest.py            # write notes
python3 System/Telegram/ingest.py --dry-run  # preview only
```

A note appears in `References/Telegram/` named `<first line of the message> (<original post date>)`, with `source: telegram`, `channel`, `published` (original post date), `captured`, `url` (link to the post, when the channel is public or a known private channel) and `links`. Photos are saved to `Assets/Telegram/`. Attached files such as PDFs are listed but not downloaded; save those to Zotero instead.

7. Put your own Telegram user id into `TELEGRAM_ALLOWED_USER_IDS` in `.env`, so messages from anyone else who finds the bot are ignored. To see your id, forward any message to @userinfobot, or run the ingest once with the variable empty and read `telegram_ids` in the created note (the number before `_`).

Notes:
- Telegram keeps undelivered messages for 24 hours. Run the script at least daily, or install the schedule (every 6 hours, and once at each login or wake if a run was missed) with `System/setup.sh schedule`. It fills the paths in `System/Telegram/com.jebi.telegram-ingest.plist.example`, installs it under `~/Library/LaunchAgents/`, and runs it once. `System/setup.sh unschedule` removes it.

  macOS blocks background jobs from reading `~/Documents`, `~/Desktop` and `~/Downloads`. If the vault lives there, give Python Full Disk Access once. The dialog does not accept the `python3` symlink, so the schedule runs the Python app bundle inside Apple's command line tools instead: System Settings → Privacy & Security → Full Disk Access → **+** → press ⌘⇧G, paste the path below, select `Python.app` and open.

```
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/
```
 The log is `System/.cache/telegram/ingest.log`; run the job by hand with `launchctl kickstart -k gui/$(id -u)/com.jebi.telegram-ingest`. Remove it with `launchctl bootout gui/$(id -u)/com.jebi.telegram-ingest`.
- If the Mac is off for more than 24 hours, messages forwarded in that time are not fetched. They are still in your chat with the bot: forward them to the bot again.
- State (last processed update, message → note mapping) lives in `System/.cache/telegram/state.json` (gitignored). Deleting it does not duplicate notes that Telegram no longer holds, but recent messages may be fetched again.
- Bots cannot download files above 20 MB; such images are skipped with a warning.

## 7. AI tools

Open the vault folder as the workspace in Claude Code / Codex. `CLAUDE.md` loads `AGENTS.md`, which holds the working rules.

## Notes

- `Wiki/Index.md` and `System/ingest-log.md` are committed as empty skeletons. `System/setup.sh base` marks them so later changes stay local (`git update-index --skip-worktree Wiki/Index.md System/ingest-log.md`).
- Local, never committed: `System/Telegram/.env` (token), `System/.cache/` (fetch state, log), the launchd file in `~/Library/LaunchAgents/`, and all content folders.
