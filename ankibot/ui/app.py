from __future__ import annotations

import asyncio
import logging
import flet as ft

from ankibot.config import APP_TITLE, load_config, save_config, DEFAULT_MODEL
from ankibot.backend import FlashcardBackend, Fact  # noqa: F401 (used via attributes)
from ankibot.ui import theme, logger, builders, pipeline, preview, export, events

applog = []
class AnkibotApp:
    """
    Main UI application class (glue). Holds state and wires up split modules.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.cfg = load_config()

        # --- Logging to UI ---
        self.logger = logging.getLogger("ankibot")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        h = logger.UILogHandler(lambda msg, lvl: logger.append_log(self, msg, lvl))
        h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%H:%M:%S"))
        self.logger.addHandler(h)

        # --- Convenience ---
        self.snack = lambda msg, color=None: logger.snack(self, msg, color)

        # --- Backend / options ---
        self.backend = FlashcardBackend(self.cfg.get("api_key", ""), DEFAULT_MODEL, logger=self.logger)
        self.model_mode = self.cfg.get("model_mode", "Fast (Gemini 2.5 Flash + thinking)")
        self.reverse_card = bool(self.cfg.get("reverse", False))
        self.custom_add = str(self.cfg.get("custom_add", ""))
        self.double_check = bool(self.cfg.get("double_check", False))
        self.new_pipeline = bool(self.cfg.get("new_pipeline", False))
        self.density_level = int(self.cfg.get("density", 2))
        self.split_by_topic = bool(self.cfg.get("split_by_topic", False))
        self.selected_files: list[str] = []
        self.last_dir: str | None = None
        self.cancel_event = asyncio.Event()

        # --- View tracking (pour éviter les reconstructions inutiles) ---
        self._current_view: str = 'home'  # 'home' ou 'settings'

        # --- Data ---
        self.source_full_text: str = ""
        self.all_facts: list[Fact] = []
        self.generated_csv: str = ""
        self.verified_csv: str = ""
        self.card_rows: list[list[str]] = []  # includes header at [0]

        # --- UI controls (populated by builders) ---
        self.log_view: ft.ListView | None = None
        self.progress: ft.ProgressBar | None = None
        self.progress_label: ft.Text | None = None
        self.fact_preview: ft.DataTable | None = None
        self.cards_preview: ft.DataTable | None = None
        self.preview_tab: ft.Tabs | None = None
        self.file_status: ft.Text | None = None
        self.api_status: ft.Text | None = None
        self.stats_badge: ft.Text | None = None
        self.content_area: ft.Container = ft.Container(expand=True, animate_opacity=300)
        
        # --- New preview controls ---
        self.facts_stats: ft.Container | None = None
        self.cards_stats: ft.Container | None = None
        self.search_facts: ft.TextField | None = None
        self.search_cards: ft.TextField | None = None
        self.update_facts_view: callable | None = None
        self.update_cards_view: callable | None = None
        self.update_logs_view: callable | None = None

        # --- Theme helpers ---
        self._apply_theme = lambda: theme.apply_theme(self)
        self._palette = lambda: theme.palette(self)
        self._is_dark = lambda: theme.is_dark(self)


        # --- Attach mixins (bind methods on self) ---
        # order matters: events before builders; preview before export (builders uses preview tables)
        preview.attach(self)
        export.attach(self)
        events.attach(self)        # _on_model_change, _on_pick, _fade_to, etc.
        pipeline.attach(self)      # _start_pipeline, _pipeline, _set_stage

        # --- Builders (create pages/sections) ---
        self._build_home = lambda: builders.build_home(self)
        self._build_settings = lambda: builders.build_settings(self)
        self._build_appbar = lambda: builders.build_appbar(self)
        self._build_status_bar = lambda: builders.build_status_bar(self)

    # ---------------- Bootstrap ---------------- #
    def start(self):
        self.page.title = APP_TITLE
        self.page.padding = 22
        self._apply_theme()
        self.page.appbar = self._build_appbar()
        # First screen
        self._current_view = 'home'
        self._fade_to(self._build_home())
        self.page.add(self.content_area)
        self.page.window_maximized = True
        self.page.update()