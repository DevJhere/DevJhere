from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .charts.breakdown_card import BreakdownCard
from .charts.daily_lines import DailyLinesChart
from .extractors import default_extractor_registry
from .history import build_daily_history
from .languages import default_language_classifier
from .linebar import LineBarHistory
from .profile_stats import ProfileStats
from .render import ChartImage, ClaudeCodeSectionRenderer
from .stats import ClaudeCodeStatsCalculator
from .transcripts import TranscriptLineParser, TranscriptRepository

WINDOW_DAYS = 30
HISTORY_DAYS = 120
SECTION_NAME = "claude-code"
ASSETS_DIR = "assets"
HOME = Path.home()
PROJECTS_DIR = HOME / ".claude" / "projects"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local")) / "profile-readme"
CACHE_FILE = DATA_DIR / "transcripts.json"
LINEBAR_STATS_FILE = DATA_DIR / "history.json"  # optional archive of older days
CLONE_DIR = DATA_DIR / "DevJhere"
REMOTE_URL = "https://github.com/DevJhere/DevJhere.git"
BRANCH = "main"


@dataclass(frozen=True)
class ClaudeCodeSection:
    markdown: str
    charts: list[ChartImage]


def build_claude_code_section(today: date) -> ClaudeCodeSection:
    stats = collect_profile_stats(today)
    charts = [
        ChartImage(f"{ASSETS_DIR}/{renderer.file_name}", renderer.render(stats), renderer.describe(stats))
        for renderer in (DailyLinesChart(), BreakdownCard())
    ]
    return ClaudeCodeSection(ClaudeCodeSectionRenderer().render(charts, today), charts)


def collect_profile_stats(today: date) -> ProfileStats:
    repository = TranscriptRepository(PROJECTS_DIR, CACHE_FILE, TranscriptLineParser(default_extractor_registry()))
    recent = ClaudeCodeStatsCalculator(default_language_classifier(), WINDOW_DAYS).summarize(
        repository.load(WINDOW_DAYS), today
    )
    history = build_daily_history(
        LineBarHistory(LINEBAR_STATS_FILE).daily_lines(), recent.first_day, recent.lines_per_day, HISTORY_DAYS
    )
    return ProfileStats(recent, history)
