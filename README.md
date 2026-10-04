# zotero-obsidian-llm-wiki

An Obsidian LLM wiki setup for economics writing: collect and highlight sources in Zotero, bring them into Obsidian with ZotLit, and let an AI maintain a wiki from your source notes and drafts.

This repository holds the **setup only** (structure, AI rules, templates, settings). Content stays local. To rebuild it on a new machine, follow [System/SETUP.md](System/SETUP.md).

## Structure

| Step | Where | Who writes |
| --- | --- | --- |
| 1 Collect | Zotero, or any other way (e.g. a PDF saved directly) | You: save sources, highlight by color, add comments |
| 2 Source notes | `References/` | ZotLit (copies Zotero items and highlights into Obsidian) or you |
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
