from __future__ import annotations

from PythonProject3.Game.ApexNews import ApexNews
from PythonProject3.Game.DeadlockNews import DeadlockNews, _parse_date
from PythonProject3.Game.GamingNews import ArcRaidersNews
from PythonProject3.Game.LeagueNews import LeagueNews


def test_arc_raiders_parser_extracts_news_cards():
    html = """
    <html><body>
      <a class="news-article-card_container__xsniv" href="/news/update-1">
        <div class="news-article-card_title__7LpPs">Update 1</div>
        <div class="news-article-card_date__fJqI_">June 23, 2026</div>
      </a>
      <a class="news-article-card_container__xsniv" href="/about">About</a>
    </body></html>
    """

    parser = ArcRaidersNews()
    items = parser.get_news(html)

    assert len(items) == 1
    assert items[0]["title"] == "Update 1"
    assert items[0]["date"] == "June 23, 2026"
    assert items[0]["link"] == "https://arcraiders.com/news/update-1"


def test_league_parser_prefers_iso_datetime_attribute():
    html = """
    <html><body>
      <a data-testid="articlefeaturedcard-component" href="/en-us/news/game-updates/patch-14-2-notes/">
        <div data-testid="card-title">Patch 14.2 Notes</div>
        <time datetime="2026-06-23T10:00:00Z">ignored text</time>
      </a>
    </body></html>
    """

    parser = LeagueNews()
    items = parser.get_news(html)

    assert len(items) == 1
    assert items[0]["title"] == "Patch 14.2 Notes"
    assert items[0]["date"] == "June 23, 2026"
    # pyrefly: ignore [missing-attribute]
    assert items[0]["link"].startswith("https://www.leagueoflegends.com/")


def test_apex_parser_requires_news_link_title_and_date():
    html = """
    <html><body>
      <a href="/games/apex-legends/apex-legends/news/season-update">
        <h3>Season Update</h3>
        <span>Published June 23, 2026</span>
      </a>
      <a href="/games/apex-legends/apex-legends/">No title/date</a>
    </body></html>
    """

    parser = ApexNews()
    items = parser.get_news(html)

    assert len(items) == 1
    assert items[0] == {
        "title": "Season Update",
        "date": "June 23, 2026",
        "link": "https://www.ea.com/games/apex-legends/apex-legends/news/season-update",
    }


def test_deadlock_parser_extracts_title_date_and_link():
    html = """
    <div class="apphub_PostSummaryFull">
      <a class="apphub_CardContentPreviewImageLink" href="https://store.steampowered.com/news/app/1422450/view/123"></a>
      <div class="apphub_CardContentTitle">Hotfix</div>
      <div class="apphub_PostSummaryDate">Jun 23, 2026</div>
    </div>
    """

    parser = DeadlockNews()
    items = parser.get_news(html)

    assert len(items) == 1
    assert items[0]["title"] == "Hotfix"
    assert items[0]["date"] == "June 23, 2026"
    assert items[0]["link"].endswith("/view/123")


def test_parse_date_normalizes_supported_formats():
    assert _parse_date("Jun 10, 2025") == "June 10, 2025"
    assert _parse_date("10 June, 2025") == "June 10, 2025"


def test_parse_date_returns_original_when_unknown_format():
    assert _parse_date("Yesterday") == "Yesterday"