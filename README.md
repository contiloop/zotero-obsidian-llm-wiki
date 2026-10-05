# zotero-obsidian-llm-wiki

An Obsidian LLM wiki setup for economics writing: collect and highlight sources in Zotero, bring them into Obsidian with ZotLit, and let an AI maintain a wiki from your source notes and drafts.

This repository holds the **setup only** (structure, AI rules, templates, settings). Content stays local. To rebuild it on a new machine, clone and run `System/setup.sh`; it does what can be automated and lists the rest. Details in [System/SETUP.md](System/SETUP.md).

## Structure

| Step | Where | Who writes |
| --- | --- | --- |
| 1 Collect | Zotero, Telegram (forward to your bot), or any other way (e.g. a PDF saved directly) | You: save sources, highlight by color, add comments |
| 2 Source notes | `References/` | ZotLit (copies Zotero items and highlights into Obsidian), the Telegram ingest script, or you |
| 3 Drafts | `Writing/Drafts/`, one folder per article | You: write thoughts with sources and evidence |
| 4 Published | `Writing/Published/` | You |
| Wiki | `Wiki/` | AI, on request, from source notes and drafts; you may also edit |

```
Collect → References → Wiki ← Drafts → Published
                              (your views)
```

## Folders

```
├── README.md            this file
├── AGENTS.md            AI working rules (CLAUDE.md loads it)
├── References/Zotero/   literature notes created by ZotLit
├── References/Telegram/ source notes created from forwarded Telegram messages
├── Wiki/Index.md        wiki index
├── Writing/Drafts/      one folder per article (free format)
├── Writing/Published/   published articles
├── Assets/              images, charts, raw data
└── System/
    ├── SETUP.md         rebuild this setup on a new machine
    ├── Templates/       Obsidian templates (Wiki)
    ├── ZotLit/          ZotLit templates (color-grouped highlights, title-based file names)
    ├── Library.base     library view of sources, wiki and writing
    └── ingest-log.md    wiki update log
```

## Highlight colors

| Color | Meaning |
| --- | --- |
| Yellow | Key claims |
| Red | Data & figures (citable evidence) |
| Green | For my writing |
| Blue | Definitions & concepts |
| Purple | Counterpoints & questions |
| Orange | Outlook & forecasts |

Literature notes group highlights under these headings; other colors go under "Other colors". Comments appear as **Note:**.

## Telegram

Forward a message to your own private Telegram bot, then run `python3 System/Telegram/ingest.py`. Each forwarded message (or album) becomes a note in `References/Telegram/` with the channel, original date, link to the post, every URL in the text, and the images saved to `Assets/Telegram/`. A plain text you send right after a forward is attached as **Note:**. Setup in [System/SETUP.md](System/SETUP.md).

## Tools

| Tool | Version tested |
| --- | --- |
| Obsidian | 1.13.7 |
| ZotLit (Obsidian plugin) | 2.1.4 |
| ZotLit Companion (Zotero plugin) | 2.1.4 |
| Zotero | 10.0.5 |
| Better BibTeX | 9.0.63 |
| Python (for the Telegram script, standard library only) | 3.14 |
