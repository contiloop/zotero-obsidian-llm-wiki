"""Run:  python3 -m unittest discover -s System/Telegram/tests  (from the vault root)"""
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from telegram_ingest.domain import (group_captures, is_bot_command, note_title, origin_url, parse_message,  # noqa: E402
                                    render_note, sanitize_filename)

T0 = 1_759_650_000  # 2026-10-05 UTC
ME = {"id": 42, "first_name": "Me"}
CHAT = {"id": 42, "type": "private"}


def fwd_channel(mid, text, ts=T0, **extra):
    m = {"message_id": mid, "date": ts, "chat": CHAT, "from": ME, "text": text,
         "forward_origin": {"type": "channel", "date": ts - 3600,
                            "chat": {"id": -1001234567890, "type": "channel", "title": "경제 뉴스", "username": "econnews"},
                            "message_id": 999}}
    m.update(extra)
    return m


class ParseTests(unittest.TestCase):
    def test_channel_forward_with_links(self):
        text = "한국은행 기준금리 2.50% 유지 https://example.com/a 자세히"
        msg = fwd_channel(1, text, entities=[{"type": "url", "offset": 20, "length": 21},
                                             {"type": "text_link", "offset": 0, "length": 4, "url": "https://bok.or.kr"}])
        cap = parse_message(msg)
        self.assertTrue(cap.is_forward)
        self.assertEqual(cap.origin_name, "경제 뉴스")
        self.assertEqual(origin_url(cap), "https://t.me/econnews/999")
        self.assertIn("https://example.com/a", cap.links)
        self.assertIn("https://bok.or.kr", cap.links)

    def test_private_channel_url(self):
        msg = fwd_channel(1, "x")
        del msg["forward_origin"]["chat"]["username"]
        self.assertEqual(origin_url(parse_message(msg)), "https://t.me/c/1234567890/999")

    def test_photo_picks_largest(self):
        msg = fwd_channel(1, "", photo=[{"file_id": "s", "file_size": 10, "width": 90},
                                        {"file_id": "l", "file_size": 500, "width": 1280}])
        msg["caption"] = "차트"
        cap = parse_message(msg)
        self.assertEqual(cap.photos[0].file_id, "l")
        self.assertEqual(cap.text, "차트")

    def test_hidden_user(self):
        msg = {"message_id": 3, "date": T0, "chat": CHAT, "from": ME, "text": "hi",
               "forward_origin": {"type": "hidden_user", "date": T0, "sender_user_name": "Someone"}}
        cap = parse_message(msg)
        self.assertEqual(cap.origin_name, "Someone")
        self.assertEqual(origin_url(cap), "")


class CommandTests(unittest.TestCase):
    def test_commands_are_not_sources(self):
        cmd = parse_message({"message_id": 1, "date": T0, "chat": CHAT, "from": ME, "text": "/clear"})
        memo = parse_message({"message_id": 2, "date": T0, "chat": CHAT, "from": ME, "text": "/usr/bin is a path, not a command"})
        self.assertTrue(is_bot_command(cmd))
        self.assertFalse(is_bot_command(memo))
        self.assertFalse(is_bot_command(parse_message(fwd_channel(3, "/start of something"))))


class GroupingTests(unittest.TestCase):
    def test_album_and_follow_up_comment(self):
        caps = [parse_message(fwd_channel(1, "", media_group_id="g1", photo=[{"file_id": "a", "file_size": 1}])),
                parse_message(fwd_channel(2, "앨범 설명", ts=T0 + 1, media_group_id="g1", photo=[{"file_id": "b", "file_size": 1}])),
                parse_message({"message_id": 3, "date": T0 + 60, "chat": CHAT, "from": ME, "text": "내 생각: 과장됨"}),
                parse_message(fwd_channel(4, "다른 글", ts=T0 + 5000)),
                parse_message({"message_id": 5, "date": T0 + 9000, "chat": CHAT, "from": ME, "text": "단독 메모"})]
        notes = group_captures(caps, 180)
        self.assertEqual(len(notes), 3)
        self.assertEqual(len(notes[0].captures), 2)
        self.assertEqual(len(notes[0].photos), 2)
        self.assertEqual(notes[0].comments, ["내 생각: 과장됨"])
        self.assertEqual(notes[1].comments, [])
        self.assertFalse(notes[2].head.is_forward)

    def test_reply_comment_targets_right_note(self):
        caps = [parse_message(fwd_channel(1, "첫 글")),
                parse_message(fwd_channel(2, "둘째 글", ts=T0 + 10)),
                parse_message({"message_id": 3, "date": T0 + 20, "chat": CHAT, "from": ME, "text": "첫 글 코멘트",
                               "reply_to_message": {"message_id": 1}})]
        notes = group_captures(caps, 180)
        self.assertEqual(notes[0].comments, ["첫 글 코멘트"])
        self.assertEqual(notes[1].comments, [])


class RenderTests(unittest.TestCase):
    def test_title_and_frontmatter(self):
        long = "미국 9월 고용지표: 비농업 신규고용 15만명, 실업률 4.3%로 상승하며 시장 예상치를 크게 벗어난 결과가 나왔다 https://x.y/z"
        note = group_captures([parse_message(fwd_channel(1, long))], 180)[0]
        note.comments.append("내 코멘트")
        title = note_title(note)
        self.assertTrue(title.startswith("미국 9월 고용지표 - 비농업"))  # first line only, colon sanitized
        self.assertNotIn("경제 뉴스", title)
        self.assertRegex(title, r"… \(\d{4}-\d{2}-\d{2}\)$")
        self.assertNotIn("https", title)
        md = render_note(note, title, ["Assets/Telegram/x.jpg"], datetime(2026, 10, 5))
        self.assertIn("source: telegram", md)
        self.assertIn('channel: 경제 뉴스', md)
        self.assertIn("url: https://t.me/econnews/999", md)
        self.assertIn("captured: 2026-10-05", md)
        self.assertIn("> [!quote]", md)
        self.assertIn("![[Assets/Telegram/x.jpg]]", md)
        self.assertIn("**Note:** 내 코멘트", md)
        self.assertIn("  - https://x.y/z", md)

    def test_bracketed_first_line(self):
        note = group_captures([parse_message(fwd_channel(1, "[조선 업종 밸류에이션]\n\n10월 2일 종가 기준"))], 180)[0]
        self.assertRegex(note_title(note), r"^조선 업종 밸류에이션 \(\d{4}-\d{2}-\d{2}\)$")

    def test_sanitize(self):
        self.assertEqual(sanitize_filename('a/b:c?d*e"f<g>h|i#j^k[l]m'), "a-b -cdefgh-ijk(l)m")


if __name__ == "__main__":
    unittest.main()
