from __future__ import annotations

import os
import re
import flet as ft

# =============================================================
# Modern, clean, dashboard-style UI for Ankibot
# - Two-pane layout on Home: left controls / right workspace
# - Three tabs in workspace: Facts, Cards, Logs
# - Split Settings: left preferences / right live preview
# - Interactive Status Bar with compact stats and API state
# =============================================================


# ---------------------------- Helpers ---------------------------- #

def _stat_chip(text: str, color: str, icon: str | None = None) -> ft.Container:
    """Compact rounded chip for status bar metrics."""
    content = [ft.Text(text, size=12, color=color, weight=ft.FontWeight.W_500)]
    if icon:
        content.insert(0, ft.Icon(icon, size=14, color=color))
    return ft.Container(
        content=ft.Row(content, spacing=6, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=color + "20",  # translucent backdrop
        padding=ft.padding.symmetric(8, 6),
        border_radius=999,
    )


def _card(
    content: ft.Control,
    *,
    pal: dict,
    padding: int = 20,
    radius: int = 20,
    alt: bool = False,
    expand: bool | int = False,
) -> ft.Container:
    bg = pal["surface_alt"] if alt else pal["surface"]
    return ft.Container(
        bgcolor=bg,
        border_radius=radius,
        padding=padding,
        shadow=ft.BoxShadow(blur_radius=20, color=pal["shadow"]),
        content=content,
        expand=expand,
    )


# ------------------------- Top App Bar ------------------------- #

def build_appbar(app) -> ft.AppBar:
    pal = app._palette()
    return ft.AppBar(
        title=ft.Row([
            ft.Text("⚡", size=20),
            ft.Text("Ankibot", color=pal["text"], size=20, weight=ft.FontWeight.W_600),
        ], spacing=8, alignment=ft.MainAxisAlignment.START),
        bgcolor=pal["surface"],
        center_title=False,
        elevation=0,
        actions=[
            ft.IconButton(
                ft.Icons.HOME,
                tooltip="Accueil",
                icon_color=pal["muted"],
                on_click=lambda e: app._go_home(),
            ),
            ft.IconButton(
                ft.Icons.SETTINGS,
                tooltip="Paramètres",
                icon_color=pal["muted"],
                on_click=lambda e: app._fade_to(build_settings(app)),
            ),
            ft.IconButton(
                ft.Icons.DARK_MODE if app._is_dark() else ft.Icons.LIGHT_MODE,
                tooltip="Basculer thème",
                icon_color=pal["muted"],
                on_click=app._toggle_theme,
            ),
            ft.IconButton(
                ft.Icons.EXIT_TO_APP,
                tooltip="Quitter",
                icon_color=pal["muted"],
                on_click=lambda e: app.page.window.close(),
            ),
        ],
    )


# ------------------------- Status Bar ------------------------- #

def build_status_bar(app) -> ft.Control:
    pal = app._palette()

    # dynamic texts stored on app for updates elsewhere in the app
    app.file_status = ft.Text("📂 Aucun fichier", color=pal["muted"], size=12)
    app.api_status = ft.Text(
        "🔑 API: Connectée" if app.cfg.get("api_key") else "🔑 API: Non connectée",
        color=pal["ok"] if app.cfg.get("api_key") else pal["err"],
        size=12,
        weight=ft.FontWeight.W_500,
    )
    app.stats_badge = ft.Text("", size=12, color=pal["muted"])  # e.g., "42 faits • 36 cartes"

    left = ft.Row([
        _stat_chip("Fichiers", pal["muted"], ft.Icons.ATTACH_FILE),
        app.file_status,
    ], spacing=10)

    middle = ft.Row([
        _stat_chip("Stats", pal["muted"], ft.Icons.ANALYTICS_OUTLINED),
        app.stats_badge,
    ], spacing=10)

    right = ft.Row([
        _stat_chip("API", pal["muted"], ft.Icons.VPN_KEY),
        app.api_status,
    ], spacing=10)

    return ft.Container(
        content=ft.Row([left, middle, right], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(14, 10),
        bgcolor=pal["surface_alt"],
        border_radius=12,
    )


# --------------------------- Home --------------------------- #

def build_home(app) -> ft.Control:
    pal = app._palette()

    # ----- Controls (Sidebar) ----- #
    model_dd = ft.Dropdown(
        label="Modèle IA",
        options=[
            ft.dropdown.Option("Ultra Fast (Gemini 2.5 Flash)"),
            ft.dropdown.Option("Fast (Gemini 2.5 Flash + thinking)"),
            ft.dropdown.Option("Smart (Gemini 2.5 Pro + thinking)"),
            ft.dropdown.Option("Fast advanced (Gemini 3.0 Flash)"),
            ft.dropdown.Option("Advanced (Gemini 3.0 Flash + thinking)"),
            ft.dropdown.Option("Smart advanced (Gemini 3.0 Pro + thinking)"),
        ],
        value=app.model_mode,
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(size=14, color=pal["text"]),
        on_change=app._on_model_change,
    )

    density_label = ft.Text("Normal", size=12, color=pal["muted"])
    density_slider = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        value=app.density_level,
        width=300,
        active_color=pal["accent"],
        on_change=lambda e: app._update_density(e, density_label),
    )

    reverse_sw = ft.Switch(
        label="Créer des cartes inversées",
        value=app.reverse_card,
        active_color=pal["accent"],
        on_change=lambda e: setattr(app, "reverse_card", e.control.value),
    )
    split_sw = ft.Switch(
        label="Séparer les decks par topic",
        value=app.split_by_topic,
        active_color=pal["accent"],
        on_change=lambda e: setattr(app, "split_by_topic", e.control.value),
    )
    double_check = ft.Switch(
        label="Vérification double",
        value=app.double_check,
        active_color=pal["accent"],
        on_change=lambda e: setattr(app, "double_check", e.control.value),
    )
    new_pipeline = ft.Switch(
        label="Nouveau pipeline",
        value=app.new_pipeline,
        active_color=pal["accent"],
        on_change=lambda e: setattr(app, "new_pipeline", e.control.value),
    )

    # Batch file picker
    fp = ft.FilePicker(on_result=app._on_pick)
    app.page.overlay.append(fp)
    pick_btn = ft.FilledButton(
        content=ft.Row([ft.Icon(ft.Icons.UPLOAD_FILE), ft.Text("Importer PDF/TXT", size=14)]),
        width=300,
        style=ft.ButtonStyle(bgcolor={"": pal["accent"], "hovered": pal["accent_hover"]}, color=ft.Colors.WHITE),
        on_click=lambda e: fp.pick_files(allow_multiple=True, allowed_extensions=["pdf", "txt"]),
    )

    # Inline text input
    text_area = ft.TextField(
        label="Ou colle du texte brut ici (facultatif)",
        multiline=True,
        min_lines=6,
        max_lines=10,
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        hint_text="Colle le texte ici si tu n'utilises pas de fichier",
    )

    custom_add_field = ft.TextField(
    label="Règles personnalisées (optionnel)",
    multiline=True,
    min_lines=2,
    max_lines=4,
    width=300,
    border_radius=12,
    text_style=ft.TextStyle(color=pal["text"], size=14),
    hint_text="Ex: Toujours inclure les dates historiques...",
    on_change=lambda e: setattr(app, "custom_add", e.control.value),
    )

    # Run / Cancel / Export
    app.progress = ft.ProgressBar(width=300, color=pal["accent"], bgcolor="#00000010", height=6)
    app.progress_label = ft.Text("", color=pal["muted"], size=12)

    run_btn = ft.FilledButton(
        content=ft.Row([ft.Icon(ft.Icons.FLASH_ON), ft.Text("Générer les flashcards", size=14)]),
        width=300,
        style=ft.ButtonStyle(bgcolor={"": pal["accent"], "hovered": pal["accent_hover"]}, color=ft.Colors.WHITE),
        on_click=lambda e: app.page.run_task(app._start_pipeline, text_area.value),
    )
    cancel_btn = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.CANCEL), ft.Text("Annuler", size=14)]),
        width=300,
        on_click=lambda e: app.cancel_event.set(),
    )
    export_btn = ft.FilledButton(
        content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD), ft.Text("Exporter", size=14)]),
        width=300,
        style=ft.ButtonStyle(bgcolor={"": pal["accent"], "hovered": pal["accent_hover"]}, color=ft.Colors.WHITE),
        on_click=lambda e: app.page.run_task(app._save_outputs),
    )

    controls = _card(
        pal=pal,
        content=ft.Column(
            [
                ft.Text("⚙️ Contrôles", size=18, weight=ft.FontWeight.W_600, color=pal["text"]),
                ft.Divider(color=pal["border"], height=16, thickness=1),
                model_dd,
                ft.Row(
                    [ft.Text("Densité des cartes", size=13, color=pal["text"]), density_label],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                density_slider,
                reverse_sw,
                split_sw,
                double_check,
                new_pipeline,
                ft.Divider(color=pal["border"], height=20, thickness=1),
                pick_btn,
                text_area,
                custom_add_field,
                run_btn,
                cancel_btn,
                export_btn,
                app.progress,
                app.progress_label,
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.START,
        ),
    )
    controls.width = 340

    # ----- Workspace (Tabs + Tables + Logs) ----- #
    app.log_view = ft.ListView(expand=True, spacing=6, auto_scroll=True, padding=12)

    # Data tables
    app.fact_preview = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Topic")),
            ft.DataColumn(ft.Text("Subtopic")),
            ft.DataColumn(ft.Text("Fact")),
            ft.DataColumn(ft.Text("Source")),
        ],
        rows=[],
    )

    app.cards_preview = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Topic")),
            ft.DataColumn(ft.Text("Subtopic")),
            ft.DataColumn(ft.Text("Question")),
            ft.DataColumn(ft.Text("Answer")),
            ft.DataColumn(ft.Text("Source")),
            ft.DataColumn(ft.Text("Details")),
            ft.DataColumn(ft.Text("Edit")),
            ft.DataColumn(ft.Text("Delete")),
        ],
        rows=[],
    )

    app.preview_tab = ft.Tabs(
        tabs=[ft.Tab(text="Faits"), ft.Tab(text="Cartes"), ft.Tab(text="Logs")],
        selected_index=0,
        expand=True,
    )

    # stack to flip visibility on tab change
    tab_stack = ft.Stack([
        ft.Container(content=ft.ListView([app.fact_preview], spacing=0, auto_scroll=False), visible=True, height=420),
        ft.Container(content=ft.ListView([app.cards_preview], spacing=0, auto_scroll=False), visible=False, height=420),
        ft.Container(content=app.log_view, visible=False, height=420),
    ])

    def on_tab_change(_e: ft.ControlEvent):
        idx = app.preview_tab.selected_index
        tab_stack.controls[0].visible = idx == 0
        tab_stack.controls[1].visible = idx == 1
        tab_stack.controls[2].visible = idx == 2
        app.page.update()

    app.preview_tab.on_change = on_tab_change

    workspace = _card(
        pal=pal,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("👁️\u200d🗨️ Aperçu", size=18, weight=ft.FontWeight.W_600, color=pal["text"]),
                        ft.Container(expand=True),
                        ft.Text("Astuce: double-clique sur ✏️ pour éditer avant l'export", size=12, color=pal["muted"]),
                    ]
                ),
                app.preview_tab,
                ft.Container(tab_stack, expand=True, padding=ft.padding.only(top=8)),
            ],
            spacing=10,
            expand=True,
        ),
        expand=True,
    )

    # ----- Title banner ----- #
    hero = _card(
        pal=pal,
        content=ft.Column(
            [
                ft.Text("⚡ Ankibot", size=30, weight=ft.FontWeight.W_700, color=pal["text"]),
                ft.Text("Convertis tes PDF en flashcards Anki automatiquement", size=14, color=pal["muted"]),
            ],
            spacing=6,
        ),
        padding=26,
        radius=22,
    )

    layout = ft.Column(
        [
            hero,
            ft.Row([controls, workspace], spacing=20, expand=True),
            build_status_bar(app),
        ],
        spacing=18,
        expand=True,
        scroll="auto",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return layout


# -------------------------- Settings -------------------------- #

def build_settings(app) -> ft.Control:
    pal = app._palette()

    # ---- Sidebar: Preferences ---- #
    api_field = ft.TextField(
        label="Clé API",
        value=app.cfg.get("api_key", ""),
        password=True,
        can_reveal_password=True,
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
    )

    theme_dd = ft.Dropdown(
        label="Thème",
        options=[
            ft.dropdown.Option("system"),
            ft.dropdown.Option("light"),
            ft.dropdown.Option("dark"),
        ],
        value=app.cfg.get("theme", "system"),
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"]),
        on_change=lambda e: app._set_theme(e.control.value),
    )

    accent_field = ft.TextField(
        label="Couleur d'accent (#40C4FF)",
        value=app.cfg.get("accent", "#40C4FF"),
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        on_change=lambda e: app._set_accent(e.control.value),
    )

    # optional extras for modern feel
    lang_dd = ft.Dropdown(
        label="Langue",
        options=[ft.dropdown.Option("fr"), ft.dropdown.Option("en")],
        value=getattr(app, "language", "fr"),
        width=300,
        border_radius=12,
        text_style=ft.TextStyle(size=14, color=pal["text"]),
        on_change=lambda e: setattr(app, "language", e.control.value),
    )

    font_slider_val = getattr(app, "font_size", 14)
    font_val_txt = ft.Text(str(font_slider_val), size=12, color=pal["muted"])
    font_slider = ft.Slider(
        min=12,
        max=22,
        divisions=10,
        value=font_slider_val,
        width=300,
        active_color=pal["accent"],
        on_change=lambda e: (setattr(app, "font_size", int(e.control.value)), setattr(font_val_txt, "value", str(int(e.control.value))), app.page.update()),
    )

    def save_click(_):
        from ankibot.config import save_config  # local import to avoid cycles
        app.cfg["api_key"] = api_field.value.strip()
        save_config(app.cfg)
        # Rebuild backend with new key, keep model
        app.backend = app.backend.__class__(app.cfg.get("api_key", ""), model=app.backend.cfg.model)
        app._apply_theme()
        app.page.appbar = build_appbar(app)
        app.content_area.content = build_settings(app)
        app.snack("Paramètres enregistrés")

    def reset_click(_):
        api_field.value = ""
        theme_dd.value = "system"
        accent_field.value = "#40C4FF"
        lang_dd.value = "fr"
        setattr(app, "font_size", 14)
        font_slider.value = 14
        font_val_txt.value = "14"
        app.page.update()
        app.snack("Paramètres réinitialisés (non enregistrés)")

    save_btn = ft.FilledButton(
        content=ft.Row([ft.Icon(ft.Icons.SAVE), ft.Text("Enregistrer", size=14)]),
        width=300,
        style=ft.ButtonStyle(bgcolor={"": pal["accent"], "hovered": pal["accent_hover"]}, color=ft.Colors.WHITE),
        on_click=save_click,
    )

    reset_btn = ft.OutlinedButton(
        content=ft.Row([ft.Icon(ft.Icons.RESTART_ALT), ft.Text("Réinitialiser", size=14)]),
        width=300,
        on_click=reset_click,
    )

    sidebar = _card(
        pal=pal,
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color=pal["text"]),
                    ft.Text("Préférences", size=20, weight=ft.FontWeight.W_700, color=pal["text"]),
                ], spacing=10),
                ft.Divider(color=pal["border"], height=20, thickness=1),
                theme_dd,
                accent_field,
                lang_dd,
                ft.Row([ft.Text("Taille police", size=14, color=pal["text"]), font_val_txt], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                font_slider,
                api_field,
                save_btn,
                reset_btn,
            ],
            spacing=16,
        ),
    )
    sidebar.width = 340

    # ---- Live Preview ---- #
    def _preview_card() -> ft.Container:
        size = getattr(app, "font_size", 14)
        return ft.Container(
            bgcolor=pal["surface"],
            padding=20,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=15, color=pal["shadow"]),
            content=ft.Column(
                [
                    ft.Text("Exemple de carte", size=size + 2, weight=ft.FontWeight.W_600, color=pal["text"]),
                    ft.Text("Q : Quelle est la capitale de la France ?", size=size, color=pal["text"]),
                    ft.Text("A : Paris", size=size, color=pal["accent"], weight=ft.FontWeight.W_600),
                ],
                spacing=10,
            ),
        )

    app.preview_card_container = _preview_card()

    workspace = _card(
        pal=pal,
        expand=True,
        content=ft.Column(
            [
                ft.Text("👀 Aperçu en direct", size=18, weight=ft.FontWeight.W_600, color=pal["text"]),
                ft.Divider(color=pal["border"], height=16, thickness=1),
                app.preview_card_container,
            ],
            spacing=16,
            expand=True,
        ),
    )

    return ft.Column([
        ft.Row([sidebar, workspace], spacing=20, expand=True),
        build_status_bar(app),
    ], spacing=18, expand=True)
