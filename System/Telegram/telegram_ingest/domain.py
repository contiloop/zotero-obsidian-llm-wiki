"""Pure logic: Bot API message dicts -> Capture -> Note -> markdown. No I/O here."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

TITLE_MAX = 60
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


@dataclass
class Attachment:
    file_id: str
    kind: str                     # "photo" | "document"
    suggested_name: str
    mime: str = ""
    size: int = 0


@dataclass
class Capture:
    """One Telegram message as received by the bot."""
    chat_id: int
    message_id: int
    date: datetime                # local time
    from_user_id: Optional[int]
    text: str = ""
    is_forward: bool = False
    origin_type: str = ""         # channel | user | hidden_user | chat
    origin_name: str = ""
    origin_username: str = ""
    origin_chat_id: Optional[int] = None
    origin_message_id: Optional[int] = None
    origin_date: Optional[datetime] = None
    photos: List[Attachment] = field(default_factory=list)
    documents: List[Attachment] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    media_group_id: str = ""
    reply_to_message_id: Optional[int] = None

    @property
    def telegram_id(self) -> str:
        return f"{self.chat_id}_{self.message_id}"


@dataclass
class Note:
    """One source note to write. Several captures merge into one (albums, follow-up comments)."""
    captures: List[Capture]
    comments: List[str] = field(default_factory=list)

    @property
    def head(self) -> Capture:
        return self.captures[0]

    @property
    def telegram_ids(self) -> List[str]:
        return [c.telegram_id for c in self.captures]

    @property
    def text(self) -> str:
        parts = [c.text for c in self.captures if c.text]
        return "\n\n".join(parts)

    @property
    def photos(self) -> List[Attachment]:
        return [p for c in self.captures for p in c.photos]

    @property
    def documents(self) -> List[Attachment]:
        return [d for c in self.captures for d in c.documents]

    @property
    def links(self) -> List[str]:
        seen: Dict[str, None] = {}
        for c in self.captures:
            for u in c.links:
                seen.setdefault(u, None)
        return list(seen)


# ---------------------------------------------------------------- parsing

def _ts(value) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromtimestamp(int(value)).astimezone()


def _extract_links(text: str, entities: Optional[list]) -> List[str]:
    links: Dict[str, None] = {}
    for ent in entities or []:
        if ent.get("type") == "text_link" and ent.get("url"):
            links.setdefault(ent["url"], None)
        elif ent.get("type") == "url":
            off, ln = ent.get("offset", 0), ent.get("length", 0)
            # Bot API offsets count UTF-16 code units
            utf16 = text.encode("utf-16-le")
            links.setdefault(utf16[off * 2:(off + ln) * 2].decode("utf-16-le", "ignore"), None)
    for m in URL_RE.findall(text or ""):
        links.setdefault(m, None)
    return list(links)


def _display_name(user: dict) -> str:
    name = " ".join(x for x in [user.get("first_name"), user.get("last_name")] if x)
    return name or user.get("username") or str(user.get("id", ""))


def parse_message(msg: dict) -> Capture:
    """Convert one Bot API Message object to a Capture."""
    text = msg.get("text") or msg.get("caption") or ""
    entities = msg.get("entities") or msg.get("caption_entities")
    sender = msg.get("from") or {}
    cap = Capture(
        chat_id=msg["chat"]["id"],
        message_id=msg["message_id"],
        date=_ts(msg["date"]),
        from_user_id=sender.get("id"),
        text=text,
        links=_extract_links(text, entities),
        media_group_id=msg.get("media_group_id") or "",
        reply_to_message_id=(msg.get("reply_to_message") or {}).get("message_id"),
    )

    origin = msg.get("forward_origin")
    if origin:
        cap.is_forward = True
        cap.origin_type = origin.get("type", "")
        cap.origin_date = _ts(origin.get("date"))
        if cap.origin_type == "channel":
            chat = origin.get("chat", {})
            cap.origin_name = chat.get("title", "")
            cap.origin_username = chat.get("username", "")
            cap.origin_chat_id = chat.get("id")
            cap.origin_message_id = origin.get("message_id")
        elif cap.origin_type == "chat":
            chat = origin.get("sender_chat", {})
            cap.origin_name = chat.get("title", "")
            cap.origin_username = chat.get("username", "")
            cap.origin_chat_id = chat.get("id")
        elif cap.origin_type == "user":
            user = origin.get("sender_user", {})
            cap.origin_name = _display_name(user)
            cap.origin_username = user.get("username", "")
        elif cap.origin_type == "hidden_user":
            cap.origin_name = origin.get("sender_user_name", "")
    elif msg.get("forward_from_chat"):  # older Bot API shape
        chat = msg["forward_from_chat"]
        cap.is_forward = True
        cap.origin_type = "channel" if chat.get("type") == "channel" else "chat"
        cap.origin_name = chat.get("title", "")
        cap.origin_username = chat.get("username", "")
        cap.origin_chat_id = chat.get("id")
        cap.origin_message_id = msg.get("forward_from_message_id")
        cap.origin_date = _ts(msg.get("forward_date"))

    if msg.get("photo"):
        best = max(msg["photo"], key=lambda p: p.get("file_size", 0) or p.get("width", 0))
        cap.photos.append(Attachment(best["file_id"], "photo", "photo.jpg", "image/jpeg", best.get("file_size", 0)))
    doc = msg.get("document")
    if doc:
        cap.documents.append(Attachment(doc["file_id"], "document", doc.get("file_name", "file"),
                                        doc.get("mime_type", ""), doc.get("file_size", 0)))
    return cap


def is_bot_command(cap: Capture) -> bool:
    """Plain '/start', '/clear' ... typed at the bot are not sources."""
    return (not cap.is_forward and not cap.photos and not cap.documents
            and cap.text.startswith("/") and " " not in cap.text.strip() and "\n" not in cap.text)


def origin_url(cap: Capture) -> str:
    """Public link to the original post when it can be rebuilt, else empty."""
    if cap.origin_type == "channel" and cap.origin_message_id:
        if cap.origin_username:
            return f"https://t.me/{cap.origin_username}/{cap.origin_message_id}"
        if cap.origin_chat_id is not None:
            internal = str(cap.origin_chat_id)
            if internal.startswith("-100"):
                internal = internal[4:]
            return f"https://t.me/c/{internal}/{cap.origin_message_id}"
    return ""


# ---------------------------------------------------------------- grouping

def group_captures(captures: List[Capture], comment_window_seconds: int) -> List[Note]:
    """Merge captures into notes.

    Rules, in order:
    - same media_group_id as the previous note -> same note (an album)
    - a non-forwarded text that replies to a captured message -> comment on that note
    - a non-forwarded text within the comment window after the last note -> comment on it
    - anything else -> a new note
    """
    notes: List[Note] = []
    by_message: Dict[int, Note] = {}
    for cap in sorted(captures, key=lambda c: (c.date, c.message_id)):
        last = notes[-1] if notes else None
        if last and cap.media_group_id and cap.media_group_id == last.head.media_group_id:
            last.captures.append(cap)
            by_message[cap.message_id] = last
            continue
        if not cap.is_forward and not cap.photos and not cap.documents and cap.text:
            target = by_message.get(cap.reply_to_message_id) if cap.reply_to_message_id else None
            if target is None and last is not None:
                gap = (cap.date - last.captures[-1].date).total_seconds()
                if 0 <= gap <= comment_window_seconds:
                    target = last
            if target is not None:
                target.comments.append(cap.text)
                by_message[cap.message_id] = target
                continue
        note = Note(captures=[cap])
        notes.append(note)
        by_message[cap.message_id] = note
    return notes


# ---------------------------------------------------------------- rendering

_FORBIDDEN = {"/": "-", ":": " -", "?": "", "*": "", '"': "", "<": "", ">": "", "|": "-",
              "#": "", "^": "", "[": "(", "]": ")", "\\": "-"}


def sanitize_filename(title: str) -> str:
    for bad, good in _FORBIDDEN.items():
        title = title.replace(bad, good)
    title = re.sub(r"\s+", " ", title).strip().strip(".")
    return title


def note_title(note: Note) -> str:
    """First line of the message, trimmed to TITLE_MAX, plus the original post date in parentheses.
    The channel stays in the frontmatter."""
    text = note.text.strip()
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    first = URL_RE.sub("", first).strip(" -–—:·")
    m = re.fullmatch(r"[\[【<《「]\s*(.+?)\s*[\]】>》」]", first)   # "[제목]" -> "제목"
    if m:
        first = m.group(1)
    if len(first) > TITLE_MAX:
        cut = first[:TITLE_MAX]
        first = (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip(" ,.;:") + "…"
    if not first:
        kind = "Photo" if note.photos else ("File" if note.documents else "Message")
        first = f"{kind} from {note.head.origin_name or 'Telegram'}"
    date = (note.head.origin_date or note.head.date).strftime("%Y-%m-%d")
    return f"{sanitize_filename(first) or note.head.telegram_id} ({date})"


def _yaml_str(value: str) -> str:
    """Quote only when YAML would misread a plain scalar (URLs stay plain, as in ZotLit notes)."""
    if value == "":
        return '""'
    risky = (": " in value or " #" in value or value != value.strip()
             or value[0] in "-?:,[]{}#&*!|>'\"%@`"
             or value.lower() in {"yes", "no", "true", "false", "null", "~", "on", "off"})
    if risky:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def _yaml_list(values: List[str]) -> str:
    if not values:
        return "[]"
    return "\n" + "\n".join(f"  - {_yaml_str(v)}" for v in values)


def render_note(note: Note, title: str, image_paths: List[str], captured: datetime) -> str:
    """Markdown for the note. image_paths are vault-relative paths of saved photos."""
    head = note.head
    published = head.origin_date or head.date
    url = origin_url(head)
    channel = head.origin_name if head.is_forward else "(own message)"
    author = head.origin_name if head.origin_type in {"user", "hidden_user"} else ""
    if head.origin_type == "channel" and head.origin_username:
        author = f"@{head.origin_username}"

    fm = [
        "---",
        f"title: {_yaml_str(title)}",
        "source: telegram",
        f"channel: {_yaml_str(channel)}",
        f"author: {_yaml_str(author)}",
        f"published: {published.strftime('%Y-%m-%d')}",
        f"captured: {captured.strftime('%Y-%m-%d')}",
        f"url: {_yaml_str(url)}",
        f"links: {_yaml_list(note.links)}",
        f"telegram_ids: {_yaml_list(note.telegram_ids)}",
        "---",
    ]

    body = [f"# {title}", ""]
    meta_line = []
    if url:
        meta_line.append(f"[Telegram]({url})")
    meta_line.append(f"{channel} · {published.strftime('%Y-%m-%d %H:%M')}")
    body.append(" · ".join(meta_line))
    body.append("")

    if note.text.strip():
        body.append("> [!quote]")
        for ln in note.text.strip().splitlines():
            body.append(f"> {ln}" if ln.strip() else ">")
        body.append("")

    for p in image_paths:
        body.append(f"![[{p}]]")
    if image_paths:
        body.append("")

    if note.documents:
        body.append("Attached files (not downloaded; save them to Zotero if needed):")
        for d in note.documents:
            size = f", {d.size // 1024} KB" if d.size else ""
            body.append(f"- {d.suggested_name}{size}")
        body.append("")

    if note.links:
        body.append("Links:")
        for u in note.links:
            body.append(f"- {u}")
        body.append("")

    for c in note.comments:
        body.append(f"**Note:** {c.strip()}")
        body.append("")

    return "\n".join(fm + [""] + body).rstrip() + "\n"


def render_comment(text: str) -> str:
    return f"\n**Note:** {text.strip()}\n"
