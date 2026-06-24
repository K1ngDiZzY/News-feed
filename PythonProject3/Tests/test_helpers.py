from __future__ import annotations

from types import SimpleNamespace

from PythonProject3.Helpers.Discord import send_to_discord, try_send
from PythonProject3.Helpers.utils import get_existing_entries


def test_get_existing_entries_returns_only_link_lines(tmp_path):
    data_file = tmp_path / "links.txt"
    data_file.write_text(
        "ArcRaidersNews_home:\n"
        "Title: One\n"
        "Link: https://example.com/1\n"
        "Date: June 23, 2026\n\n"
        "Title: Two\n"
        "Link: https://example.com/2\n",
        encoding="utf-8",
    )

    entries = get_existing_entries(str(data_file))

    assert entries == {"https://example.com/1", "https://example.com/2"}


def test_get_existing_entries_missing_file_returns_empty_set(tmp_path):
    missing = tmp_path / "missing.txt"
    assert get_existing_entries(str(missing)) == set()


def test_send_to_discord_returns_true_on_204(monkeypatch):
    def fake_post(_webhook, json):
        assert "content" in json
        return SimpleNamespace(status_code=204)

    monkeypatch.setattr("PythonProject3.Helpers.Discord.requests.post", fake_post)

    ok = send_to_discord(
        "https://discord.test/webhook",
        {"title": "t", "link": "https://x", "date": "June 23, 2026"},
    )

    assert ok is True


def test_try_send_no_webhook_skips_network():
    should_save, sent_count, failed_count = try_send(
        None,
        {"title": "t", "link": "https://x", "date": "June 23, 2026"},
        0,
        0,
    )

    assert should_save is True
    assert sent_count == 0
    assert failed_count == 0


def test_try_send_failure_increments_failed(monkeypatch):
    monkeypatch.setattr("PythonProject3.Helpers.Discord.send_to_discord", lambda *_: False)

    should_save, sent_count, failed_count = try_send(
        "https://discord.test/webhook",
        {"title": "t", "link": "https://x", "date": "June 23, 2026"},
        2,
        1,
    )

    assert should_save is False
    assert sent_count == 2
    assert failed_count == 2