from __future__ import annotations
import os
import re
import flet as ft
from ankibot.config import save_config


def attach(app):
    # ----- Navigation / theme -----
    def _go_home():
        app._fade_to(app._build_home())

    def _toggle_theme(_):
        app.cfg["theme"] = "light" if app._is_dark() else "dark"
        save_config(app.cfg)
        app._apply_theme()
        app.page.appbar = app._build_appbar()
        app._fade_to(app._build_home())

    def _set_theme(val: str):
        app.cfg["theme"] = val
        save_config(app.cfg)
        app._apply_theme()
        app.page.appbar = app._build_appbar()

    def _set_accent(val: str):
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", (val or "").strip() or "#40C4FF"):
            app.cfg["accent"] = val.strip()
            save_config(app.cfg)
            app._apply_theme()
            app.page.appbar = app._build_appbar()

    # ----- Model / density -----
    def _on_model_change(e: ft.ControlEvent):
        label = e.control.value
        app.model_mode = label
        if "2.5 Flash" in label:
            app.backend.cfg.model = "gemini-2.5-flash"
        elif "2.5 Pro" in label:
            app.backend.cfg.model = "gemini-2.5-pro"
        elif "3.0 Flash" in label:
            app.backend.cfg.model = "gemini-3.0-flash"
        elif "3.0 Pro" in label:
            app.backend.cfg.model = "gemini-3.0-pro"
        else:
            app.backend.cfg.model = "gemini-2.5-flash"
            app.logger.warn(f"Modèle inconnu sélectionné: {label}, retour à gemini-2.5-flash")
        if "thinking" in label:
            app.backend.cfg.thinking_budget = -1
        else:
            app.backend.cfg.thinking_budget = 0
        app.cfg["model_mode"] = label
        save_config(app.cfg)
        app.logger.info(f"Modèle changé → {app.backend.cfg.model} (thinking={app.backend.cfg.thinking_budget})")

    def _update_density(e: ft.ControlEvent, lbl: ft.Text):
        mapping = {1: "Faible", 2: "Normal", 3: "Élevée"}
        app.density_level = int(e.control.value)
        lbl.value = f"Densité des cartes : {mapping[app.density_level]}"
        app.cfg["density"] = app.density_level
        save_config(app.cfg)
        app.page.update()

    # ----- File picking -----
    def _on_pick(e: ft.FilePickerResultEvent):
        pal = app._palette()
        if e.files:
            app.selected_files = [f.path for f in e.files]
            app.last_dir = os.path.dirname(app.selected_files[0])
            names = ", ".join(os.path.basename(f) for f in app.selected_files[:3])
            if len(app.selected_files) > 3:
                names += f" … (+{len(app.selected_files)-3})"
            app.file_status.value = f"📂 {len(app.selected_files)} fichiers : {names}"
            app.file_status.color = pal["ok"]
            app.logger.info(f"Fichiers chargés: {', '.join(app.selected_files)}")
        else:
            app.selected_files = []
            app.file_status.value = "📂 Aucun fichier"
            app.file_status.color = pal["warn"]
        app.page.update()

    # ----- Content fade -----
    def _fade_to(content: ft.Control):
        app.content_area.opacity = 0
        app.content_area.content = content
        app.page.update()
        app.content_area.opacity = 1
        app.page.update()

    # bind
    app._go_home = _go_home
    app._toggle_theme = _toggle_theme
    app._set_theme = _set_theme
    app._set_accent = _set_accent
    app._on_model_change = _on_model_change
    app._update_density = _update_density
    app._on_pick = _on_pick
    app._fade_to = _fade_to
