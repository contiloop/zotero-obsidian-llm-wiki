"""Core use case: fetch pending messages, turn them into notes, record what was done."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .config import Config
from .domain import Capture, group_captures, is_bot_command, note_title, parse_message, render_comment, render_note, sanitize_filename
from .telegram_api import BotApi, TelegramError
from .vault import State, Vault


@dataclass
class Result:
    created: List[str] = field(default_factory=list)
    commented: List[str] = field(default_factory=list)
    rejected_senders: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _image_name(cap: Capture, index: int) -> str:
    src = cap.origin_username or sanitize_filename(cap.origin_name) or "telegram"
    src = src.replace(" ", "_")[:40]
    stamp = (cap.origin_date or cap.date).strftime("%Y-%m-%d")
    return f"{stamp}_{src}_{cap.origin_message_id or cap.message_id}_{index}.jpg"


def run(cfg: Config, api: BotApi, vault: Vault, state: State, dry_run: bool = False) -> Result:
    result = Result()
    updates = api.get_updates(state.offset)
    if not updates:
        return result

    captures: List[Capture] = []
    for upd in updates:
        msg = upd.get("message")
        if not msg:
            continue
        sender = (msg.get("from") or {}).get("id")
        if cfg.allowed_user_ids and sender not in cfg.allowed_user_ids:
            if sender not in result.rejected_senders:
                result.rejected_senders.append(sender)
            continue
        cap = parse_message(msg)
        if is_bot_command(cap):
            continue
        captures.append(cap)

    now = datetime.now().astimezone()
    captures.sort(key=lambda c: (c.date, c.message_id))

    # Comments on notes written in an earlier run: a reply to a processed message, or a plain
    # text that arrives shortly after the last note and before anything else in this batch.
    fresh: List[Capture] = []
    for cap in captures:
        is_plain_text = not cap.is_forward and not cap.photos and not cap.documents and bool(cap.text)
        target = None
        if is_plain_text:
            if cap.reply_to_message_id is not None:
                target = state.seen.get(f"{cap.chat_id}_{cap.reply_to_message_id}")
            elif not fresh and state.last_note_path and state.last_note_ts is not None:
                gap = cap.date.timestamp() - state.last_note_ts
                if 0 <= gap <= cfg.comment_window_seconds:
                    target = state.last_note_path
        if target:
            if not dry_run:
                if vault.append(target, render_comment(cap.text)) is None:
                    result.warnings.append(f"{cap.telegram_id}: note {target} no longer exists; comment dropped")
                else:
                    state.seen[cap.telegram_id] = target
                    state.last_note_path = target
                    state.last_note_ts = cap.date.timestamp()
            result.commented.append(target)
            continue
        fresh.append(cap)

    for note in group_captures(fresh, cfg.comment_window_seconds):
        image_paths: List[str] = []
        for cap in note.captures:
            for i, photo in enumerate(cap.photos, 1):
                if dry_run:
                    image_paths.append(f"Assets/Telegram/{_image_name(cap, i)}")
                    continue
                try:
                    data = api.download(photo.file_id)
                except TelegramError as e:
                    result.warnings.append(f"{cap.telegram_id}: image not downloaded ({e})")
                    continue
                image_paths.append(vault.save_asset(_image_name(cap, i), data))

        title = note_title(note)
        content = render_note(note, title, image_paths, now)
        if dry_run:
            result.created.append(f"[dry-run] {title}.md")
            continue
        path = vault.write_note(title, content)
        rel = vault.rel(path)
        for t in note.telegram_ids:
            state.seen[t] = rel
        state.last_note_path = rel
        state.last_note_ts = max(c.date.timestamp() for c in note.captures)
        result.created.append(rel)

    if not dry_run:
        state.offset = updates[-1]["update_id"] + 1
        state.save()
    return result
