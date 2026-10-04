---
type: system
---

# Setup

How to rebuild this vault's setup on a new machine (or after reinstalling). This repository contains the setup only: structure, AI rules, templates and settings. Content stays local.

## 1. Apps

| App | Version tested | Notes |
| --- | --- | --- |
| Obsidian | 1.13.7 | ZotLit needs Obsidian installer 1.13.4+ |
| Zotero | 10.0.5 | |
| Better BibTeX (Zotero plugin) | 9.0.63 | Generates citekeys |
| ZotLit Companion (Zotero plugin) | 2.1.4 | `zotlit-zotero-2.1.4.xpi` |
| ZotLit (Obsidian plugin) | 2.1.4 | |

## 2. Get the vault

```bash
git clone https://github.com/contiloop/zotero-obsidian-llm-wiki.git
```

Open the cloned folder in Obsidian with **Open folder as vault**.

## 3. ZotLit (Obsidian plugin)

Plugin code is not stored in this repository. Settings are (`.obsidian/plugins/zotlit/data.json`, `manifest.json`).

1. Download `main.js` and `styles.css` for version 2.1.4 from https://github.com/aidenlx/zotlit/releases
2. Put both files in `.obsidian/plugins/zotlit/`
3. Obsidian → Settings → Community plugins → enable **ZotLit**
4. Settings → ZotLit → Zotero database: point it to your Zotero data folder (default `~/Zotero`)
5. Settings → ZotLit → Templates → **Frontmatter**: confirm the fields below exist. If they are missing, add them with the **+** button (Language: Liquid, Merge: Replace).

| Key | Expression |
| --- | --- |
| captured | `zt.dateAdded \| date: "%Y-%m-%d"` |
| published | `zt.date \| date: "%Y-%m-%d"` |
| url | `zt.url` |

Settings already stored in this repository: literature note folder `References/Zotero`, template folder `System/ZotLit` (color-grouped highlights, title-based file names).

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

## 6. AI tools

Open the vault folder as the workspace in Claude Code / Codex. `CLAUDE.md` loads `AGENTS.md`, which holds the working rules.

## Notes

- `Wiki/Index.md` and `System/ingest-log.md` are committed as empty skeletons. To keep later changes local, run once after cloning:

```bash
git update-index --skip-worktree Wiki/Index.md System/ingest-log.md
```
