from __future__ import annotations

from datetime import datetime

from PythonProject3.Cyber.HackingNews import NewsFeed, get_existing_entries as get_cyber_existing
from PythonProject3.Game.GamingNews import ArcRaidersNews


def test_arc_save_to_file_writes_only_new_today_entries(tmp_path, monkeypatch):
    out_file = tmp_path / "arc_raiders_news.txt"
    today = datetime.now().strftime("%B %d, %Y")

    parser = ArcRaidersNews()
    parser.news = [
        {"title": "New One", "date": today, "link": "https://arcraiders.com/news/new-1"},
        {"title": "Duplicate", "date": today, "link": "https://arcraiders.com/news/dup"},
    ]

    out_file.write_text(
        "ArcRaidersNews_home:\n"
        "Title: Existing\n"
        "Link: https://arcraiders.com/news/dup\n"
        f"Date: {today}\n\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("PythonProject3.Game.GamingNews.try_send", lambda _w, _a, s, f: (True, s + 1, f))

    result = parser.save_to_file(filename=str(out_file), webhook="https://discord.test/webhook")
    saved = out_file.read_text(encoding="utf-8")

    assert result == {"sent": 1, "failed": 0}
    assert "https://arcraiders.com/news/new-1" in saved
    assert saved.count("https://arcraiders.com/news/dup") == 1


def test_arc_save_to_file_skips_write_when_send_fails(tmp_path, monkeypatch):
    out_file = tmp_path / "arc_raiders_news.txt"
    today = datetime.now().strftime("%B %d, %Y")

    parser = ArcRaidersNews()
    parser.news = [{"title": "Will Fail", "date": today, "link": "https://arcraiders.com/news/fail"}]

    monkeypatch.setattr("PythonProject3.Game.GamingNews.try_send", lambda _w, _a, s, f: (False, s, f + 1))

    result = parser.save_to_file(filename=str(out_file), webhook="https://discord.test/webhook")
    saved = out_file.read_text(encoding="utf-8")

    assert result == {"sent": 0, "failed": 1}
    assert "https://arcraiders.com/news/fail" not in saved


def test_cyber_get_existing_entries_parses_title_and_date_pairs(tmp_path):
    out_file = tmp_path / "news.txt"
    out_file.write_text(
        "\n\nbleepingcomputer:\n"
        "Title: Entry One\n"
        "Link: https://example.com/one\n"
        "Date: Tue, 23 Jun 2026 08:00:00 +0000\n\n",
        encoding="utf-8",
    )

    existing = get_cyber_existing(str(out_file))

    assert ("Entry One",
            datetime.strptime("Tue, 23 Jun 2026 08:00:00 +0000", "%a, %d %b %Y %H:%M:%S %z").date()) in existing


def test_cyber_save_to_file_skips_entry_when_send_fails(tmp_path, monkeypatch):
    out_file = tmp_path / "news.txt"
    now_str = datetime.now().astimezone().strftime("%a, %d %b %Y %H:%M:%S %z")

    monkeypatch.setattr("PythonProject3.Cyber.HackingNews.NewsFeed.get_news", lambda self: None)
    monkeypatch.setattr("PythonProject3.Cyber.HackingNews.try_send", lambda _w, _e, s, f: (False, s, f + 1))

    feed = NewsFeed()
    feed.news = {
        "bleepingcomputer": [
            {"title": "Do not write", "link": "https://example.com/drop", "date": now_str}
        ]
    }

    result = feed.save_to_file(filename=str(out_file), webhook="https://discord.test/webhook")
    saved = out_file.read_text(encoding="utf-8")

    assert result == {"sent": 0, "failed": 1}
    assert "Do not write" not in saved