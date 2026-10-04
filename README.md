# zotero-obsidian-llm-wiki

An Obsidian vault setup for economics writing: collect and highlight sources in Zotero, bring them into Obsidian with ZotLit, and let an AI grow a wiki from your drafts.

This repository holds the **setup only** (structure, AI rules, templates, settings). Content stays local. To rebuild it on a new machine, follow [System/SETUP.md](System/SETUP.md).

## Layers

| Layer | Where | Role |
| --- | --- | --- |
| 0 Collect | Zotero | Save anything that looks important, highlight by color, add comments. Used in writing or not, keep it. |
| 1 Literature notes | `References/` | One note per source: your highlights, comments and source info. Originals are never edited. |
| 2 Wiki | `Wiki/` | Topic knowledge that accumulates: compressed and connected across sources (same claim, conflict, cause, change over time), always with sources. |
| 2.5 Work notes | `Writing/Drafts/` | One folder per article: sources used and why, loose thinking, discarded evidence, outline. The connections you make yourself. |
| 3 Output | `Writing/Published/` | Published articles, frozen after publishing. |

## Flow

```
Zotero → References ──→ Drafts (you connect) → Published
              │              │
              └──→ Wiki ←────┘ (connections reusable in the next article)
                    │
                    └──→ starting point for the next Drafts
```

**The wiki is not built in advance; it grows from drafts.** A topic gets a page only when it recurs across articles or sources pile up.

## Folders

```
├── README.md            this file
├── AGENTS.md            AI working rules (CLAUDE.md loads it)
├── References/Zotero/   literature notes created by ZotLit
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

## Tools

| Tool | Version tested |
| --- | --- |
| Obsidian | 1.13.7 |
| ZotLit (Obsidian plugin) | 2.1.4 |
| ZotLit Companion (Zotero plugin) | 2.1.4 |
| Zotero | 10.0.5 |
| Better BibTeX | 9.0.63 |
