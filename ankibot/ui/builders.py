from __future__ import annotations

import flet as ft

# =============================================================
# Enhanced Modern UI for Ankibot
# - Polished design with better visual hierarchy
# - Improved color scheme and spacing
# - Better empty states and feedback
# - Smoother animations and interactions
# =============================================================


# ---------------------------- Helpers ---------------------------- #

def _stat_chip(text: str, color: str, icon: str | None = None, badge: str = "") -> ft.Container:
    """Enhanced stat chip with optional badge."""
    content = []
    if icon:
        content.append(ft.Icon(icon, size=16, color=color))
    content.append(ft.Text(text, size=13, color=color, weight=ft.FontWeight.W_600))
    if badge:
        content.append(
            ft.Container(
                content=ft.Text(badge, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.W_700),
                bgcolor=color,
                padding=ft.padding.symmetric(6, 3),
                border_radius=10,
            )
        )
    
    return ft.Container(
        content=ft.Row(content, spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=color + "15",
        padding=ft.padding.symmetric(12, 8),
        border_radius=12,
        border=ft.border.all(1, color + "30"),
    )


def _card(
    content: ft.Control,
    *,
    pal: dict,
    padding: int = 24,
    radius: int = 16,
    alt: bool = False,
    expand: bool | int = False,
    elevation: int = 2,
) -> ft.Container:
    bg = pal["surface_alt"] if alt else pal["surface"]
    blur = 12 if elevation == 1 else 24 if elevation == 2 else 32
    
    return ft.Container(
        bgcolor=bg,
        border_radius=radius,
        padding=padding,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=blur,
            color=pal["shadow"],
            offset=ft.Offset(0, elevation * 2)
        ),
        border=ft.border.all(1, pal["border"]),
        content=content,
        expand=expand,
    )


def _section_header(title: str, icon: str, pal: dict, subtitle: str = "") -> ft.Column:
    """Create a consistent section header."""
    items = [
        ft.Row([
            ft.Container(
                content=ft.Icon(icon, size=20, color=pal["accent"]),
                bgcolor=pal["accent"] + "15",
                padding=8,
                border_radius=10,
            ),
            ft.Text(title, size=20, weight=ft.FontWeight.W_700, color=pal["text"]),
        ], spacing=12)
    ]
    
    if subtitle:
        items.append(
            ft.Text(subtitle, size=13, color=pal["muted"], italic=True)
        )
    
    return ft.Column(items, spacing=6)


def _empty_state(icon: str, title: str, subtitle: str, pal: dict) -> ft.Container:
    """Beautiful empty state component."""
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=64, color=pal["muted"] + "40"),
            ft.Text(title, size=18, weight=ft.FontWeight.W_600, color=pal["muted"]),
            ft.Text(subtitle, size=13, color=pal["muted"], text_align=ft.TextAlign.CENTER),
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        alignment=ft.alignment.center,
        expand=True,
    )


# ------------------------- Top App Bar ------------------------- #

def build_appbar(app) -> ft.AppBar:
    pal = app._palette()
    
    return ft.AppBar(
        leading=ft.Container(
            content=ft.Text("⚡", size=24),
            padding=ft.padding.only(left=12),
        ),
        title=ft.Text(
            "Ankibot", 
            size=22, 
            weight=ft.FontWeight.W_700,
            color=pal["text"],
        ),
        bgcolor=pal["surface"],
        center_title=False,
        elevation=0,
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        ft.Icons.HOME_ROUNDED,
                        tooltip="Accueil",
                        icon_color=pal["text"],
                        icon_size=22,
                        style=ft.ButtonStyle(
                            overlay_color=pal["accent"] + "15",
                        ),
                        on_click=lambda e: app._go_home(),
                    ),
                    ft.IconButton(
                        ft.Icons.SETTINGS_ROUNDED,
                        tooltip="Paramètres",
                        icon_color=pal["text"],
                        icon_size=22,
                        style=ft.ButtonStyle(
                            overlay_color=pal["accent"] + "15",
                        ),
                        on_click=lambda e: app._fade_to(build_settings(app)),
                    ),
                    ft.VerticalDivider(width=1, color=pal["border"]),
                    ft.IconButton(
                        ft.Icons.DARK_MODE_ROUNDED if app._is_dark() else ft.Icons.LIGHT_MODE_ROUNDED,
                        tooltip="Basculer thème",
                        icon_color=pal["accent"],
                        icon_size=22,
                        style=ft.ButtonStyle(
                            overlay_color=pal["accent"] + "15",
                        ),
                        on_click=app._toggle_theme,
                    ),
                ], spacing=4),
                padding=ft.padding.only(right=8),
            ),
        ],
    )


# ------------------------- Status Bar ------------------------- #

def build_status_bar(app) -> ft.Control:
    pal = app._palette()

    app.file_status = ft.Text("Aucun fichier", color=pal["muted"], size=13, weight=ft.FontWeight.W_500)
    api_connected = bool(app.cfg.get("api_key"))
    app.api_status = ft.Text(
        "Connectée" if api_connected else "Non connectée",
        color=pal["ok"] if api_connected else pal["err"],
        size=13,
        weight=ft.FontWeight.W_600,
    )
    app.stats_badge = ft.Text("—", size=13, color=pal["text"], weight=ft.FontWeight.W_500)

    left = _stat_chip("Fichiers", pal["muted"], ft.Icons.FOLDER_OUTLINED)
    left_text = ft.Container(content=app.file_status, padding=ft.padding.only(left=8))

    middle = _stat_chip("Stats", pal["accent"], ft.Icons.ANALYTICS_OUTLINED)
    middle_text = ft.Container(content=app.stats_badge, padding=ft.padding.only(left=8))

    right = _stat_chip("API", pal["ok"] if api_connected else pal["err"], ft.Icons.VPN_KEY_ROUNDED)
    right_text = ft.Container(content=app.api_status, padding=ft.padding.only(left=8))

    return ft.Container(
        content=ft.Row([
            ft.Row([left, left_text], spacing=0),
            ft.Row([middle, middle_text], spacing=0),
            ft.Row([right, right_text], spacing=0),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=16,
        bgcolor=pal["surface"],
        border_radius=16,
        border=ft.border.all(1, pal["border"]),
        shadow=ft.BoxShadow(blur_radius=8, color=pal["shadow"]),
    )


# --------------------------- Home --------------------------- #

def build_home(app) -> ft.Control:
    pal = app._palette()

    # ----- Hero Banner ----- #
    hero = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("⚡", size=36),
                        ft.Text("Ankibot", size=32, weight=ft.FontWeight.W_800, color=pal["text"]),
                    ], spacing=12),
                    ft.Text(
                        "Transformez vos documents en flashcards Anki intelligemment",
                        size=15,
                        color=pal["muted"],
                        weight=ft.FontWeight.W_500,
                    ),
                ], spacing=8),
                expand=True,
            ),
            ft.Container(
                content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=48, color=pal["accent"] + "40"),
                padding=12,
                bgcolor=pal["accent"] + "10",
                border_radius=16,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=28,
        bgcolor=pal["surface"],
        border_radius=20,
        border=ft.border.all(1, pal["border"]),
        shadow=ft.BoxShadow(blur_radius=16, color=pal["shadow"]),
    )

    # ----- Controls Sidebar ----- #
    model_dd = ft.Dropdown(
        label="🤖 Modèle IA",
        options=[
            ft.dropdown.Option("Ultra Fast (Gemini 2.5 Flash)"),
            ft.dropdown.Option("Fast (Gemini 2.5 Flash + thinking)"),
            ft.dropdown.Option("Smart (Gemini 2.5 Pro + thinking)"),
            ft.dropdown.Option("Fast advanced (Gemini 3.0 Flash)"),
            ft.dropdown.Option("Advanced (Gemini 3.0 Flash + thinking)"),
            ft.dropdown.Option("Smart advanced (Gemini 3.0 Pro + thinking)"),
        ],
        value=app.model_mode,
        border_radius=12,
        text_style=ft.TextStyle(size=14, color=pal["text"]),
        bgcolor=pal["surface_alt"],
        on_change=app._on_model_change,
    )

    density_label = ft.Text("Normal", size=13, color=pal["accent"], weight=ft.FontWeight.W_600)
    density_slider = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        value=app.density_level,
        active_color=pal["accent"],
        inactive_color=pal["border"],
        thumb_color=pal["accent"],
        on_change=lambda e: app._update_density(e, density_label),
    )

    # Options section
    options_card = _card(
        pal=pal,
        alt=True,
        padding=16,
        radius=12,
        elevation=1,
        content=ft.Column([
            ft.Switch(
                label="Cartes inversées",
                value=app.reverse_card,
                active_color=pal["accent"],
                label_style=ft.TextStyle(size=14, color=pal["text"]),
                on_change=lambda e: setattr(app, "reverse_card", e.control.value),
            ),
            ft.Switch(
                label="Séparer par topic",
                value=app.split_by_topic,
                active_color=pal["accent"],
                label_style=ft.TextStyle(size=14, color=pal["text"]),
                on_change=lambda e: setattr(app, "split_by_topic", e.control.value),
            ),
            ft.Switch(
                label="Vérification double",
                value=app.double_check,
                active_color=pal["accent"],
                label_style=ft.TextStyle(size=14, color=pal["text"]),
                on_change=lambda e: setattr(app, "double_check", e.control.value),
            ),
            ft.Switch(
                label="Nouveau pipeline",
                value=app.new_pipeline,
                active_color=pal["accent"],
                label_style=ft.TextStyle(size=14, color=pal["text"]),
                on_change=lambda e: setattr(app, "new_pipeline", e.control.value),
            ),
        ], spacing=8),
    )

    # File picker
    fp = ft.FilePicker(on_result=app._on_pick)
    app.page.overlay.append(fp)
    
    pick_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=20, color=ft.Colors.WHITE),
            ft.Text("Importer des fichiers", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=pal["accent"],
        padding=14,
        border_radius=12,
        ink=True,
        on_click=lambda e: fp.pick_files(allow_multiple=True, allowed_extensions=["pdf", "txt"]),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    text_area = ft.TextField(
        label="📝 Ou collez du texte ici",
        multiline=True,
        min_lines=4,
        max_lines=8,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        hint_text="Collez votre texte directement ici...",
        border_color=pal["border"],
        focused_border_color=pal["accent"],
    )

    custom_add_field = ft.TextField(
        label="✨ Règles personnalisées (optionnel)",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        hint_text="Ex: Toujours inclure les dates...",
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        on_change=lambda e: setattr(app, "custom_add", e.control.value),
    )

    # Progress
    app.progress = ft.ProgressBar(
        color=pal["accent"],
        bgcolor=pal["border"],
        height=6,
        border_radius=3,
    )
    app.progress_label = ft.Text("", color=pal["muted"], size=13, weight=ft.FontWeight.W_500)

    # Action buttons
    run_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, size=20, color=ft.Colors.WHITE),
            ft.Text("Générer", size=15, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=pal["accent"],
        padding=16,
        border_radius=12,
        ink=True,
        on_click=lambda e: app.page.run_task(app._start_pipeline, text_area.value),
        shadow=ft.BoxShadow(blur_radius=12, color=pal["accent"] + "40", offset=ft.Offset(0, 4)),
    )

    cancel_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CANCEL_ROUNDED, size=18, color=pal["err"]),
            ft.Text("Annuler", size=14, weight=ft.FontWeight.W_600, color=pal["err"]),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="transparent",
        padding=14,
        border_radius=12,
        border=ft.border.all(2, pal["err"]),
        ink=True,
        on_click=lambda e: app.cancel_event.set(),
    )

    export_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=18, color=pal["accent"]),
            ft.Text("Exporter", size=14, weight=ft.FontWeight.W_600, color=pal["accent"]),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="transparent",
        padding=14,
        border_radius=12,
        border=ft.border.all(2, pal["accent"]),
        ink=True,
        on_click=lambda e: app.page.run_task(app._save_outputs),
    )

    controls = _card(
        pal=pal,
        elevation=2,
        content=ft.Column([
            _section_header("Contrôles", ft.Icons.TUNE_ROUNDED, pal),
            ft.Divider(color=pal["border"], height=20),
            model_dd,
            ft.Container(height=8),
            ft.Row([
                ft.Text("Densité", size=14, color=pal["text"], weight=ft.FontWeight.W_600),
                density_label,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            density_slider,
            ft.Container(height=4),
            options_card,
            ft.Container(height=12),
            pick_btn,
            text_area,
            custom_add_field,
            ft.Container(height=8),
            run_btn,
            ft.Row([cancel_btn, export_btn], spacing=12),
            ft.Container(height=4),
            app.progress,
            app.progress_label,
        ], spacing=12),
    )
    controls.width = 380

    # ----- Workspace (Tabs) ----- #
    app.log_view = ft.ListView(expand=True, spacing=4, auto_scroll=True, padding=12)

    app.fact_preview = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Topic", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Subtopic", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Fact", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Source", weight=ft.FontWeight.W_600)),
        ],
        rows=[],
        border=ft.border.all(1, pal["border"]),
        border_radius=12,
        heading_row_color=pal["surface_alt"],
    )

    app.cards_preview = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Topic", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Subtopic", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Question", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Answer", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Source", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("Details", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("✏️", weight=ft.FontWeight.W_600)),
            ft.DataColumn(ft.Text("🗑️", weight=ft.FontWeight.W_600)),
        ],
        rows=[],
        border=ft.border.all(1, pal["border"]),
        border_radius=12,
        heading_row_color=pal["surface_alt"],
    )

    # Empty states
    facts_empty = _empty_state(
        ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
        "Aucun fait généré",
        "Les faits extraits apparaîtront ici",
        pal
    )

    cards_empty = _empty_state(
        ft.Icons.STYLE_ROUNDED,
        "Aucune carte générée",
        "Les flashcards apparaîtront ici après génération",
        pal
    )

    logs_empty = _empty_state(
        ft.Icons.TERMINAL_ROUNDED,
        "Aucun log",
        "Les logs de traitement s'afficheront ici",
        pal
    )

    app.preview_tab = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        label_color=pal["accent"],
        indicator_color=pal["accent"],
        divider_color=pal["border"],
        tabs=[
            ft.Tab(
                text="Faits",
                icon=ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
            ),
            ft.Tab(
                text="Cartes",
                icon=ft.Icons.STYLE_ROUNDED,
            ),
            ft.Tab(
                text="Logs",
                icon=ft.Icons.TERMINAL_ROUNDED,
            ),
        ],
    )

    fact_container = ft.Container(
        content=ft.Stack([
            facts_empty,
            ft.ListView([app.fact_preview], spacing=0, auto_scroll=False),
        ]),
        visible=True,
        height=500,
    )

    cards_container = ft.Container(
        content=ft.Stack([
            cards_empty,
            ft.ListView([app.cards_preview], spacing=0, auto_scroll=False),
        ]),
        visible=False,
        height=500,
    )

    logs_container = ft.Container(
        content=ft.Stack([
            logs_empty,
            app.log_view,
        ]),
        visible=False,
        height=500,
    )

    def on_tab_change(_e: ft.ControlEvent):
        idx = app.preview_tab.selected_index
        fact_container.visible = idx == 0
        cards_container.visible = idx == 1
        logs_container.visible = idx == 2
        app.page.update()

    app.preview_tab.on_change = on_tab_change

    workspace = _card(
        pal=pal,
        elevation=2,
        expand=True,
        content=ft.Column([
            ft.Row([
                _section_header("Aperçu", ft.Icons.VISIBILITY_ROUNDED, pal, "Visualisez vos résultats en temps réel"),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(
                        "💡 Double-cliquez sur ✏️ pour éditer",
                        size=12,
                        color=pal["muted"],
                        italic=True,
                    ),
                    padding=8,
                    bgcolor=pal["surface_alt"],
                    border_radius=8,
                ),
            ]),
            ft.Divider(color=pal["border"], height=16),
            app.preview_tab,
            ft.Container(
                content=ft.Column([
                    fact_container,
                    cards_container,
                    logs_container,
                ]),
                padding=ft.padding.only(top=12),
                expand=True,
            ),
        ], spacing=12, expand=True),
    )

    layout = ft.Column([
        hero,
        ft.Row([controls, workspace], spacing=24, expand=True, alignment=ft.MainAxisAlignment.START),
        build_status_bar(app),
    ], spacing=24, expand=True)

    return layout


# -------------------------- Settings -------------------------- #

def build_settings(app) -> ft.Control:
    pal = app._palette()

    # API Field
    api_field = ft.TextField(
        label="🔑 Clé API Google",
        value=app.cfg.get("api_key", ""),
        password=True,
        can_reveal_password=True,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
    )

    theme_dd = ft.Dropdown(
        label="🎨 Thème",
        options=[
            ft.dropdown.Option("system", "Système"),
            ft.dropdown.Option("light", "Clair"),
            ft.dropdown.Option("dark", "Sombre"),
        ],
        value=app.cfg.get("theme", "system"),
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"]),
        bgcolor=pal["surface_alt"],
        on_change=lambda e: app._set_theme(e.control.value),
    )

    accent_field = ft.TextField(
        label="🎨 Couleur d'accent",
        value=app.cfg.get("accent", "#40C4FF"),
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        on_change=lambda e: app._set_accent(e.control.value),
    )

    # Color preview
    color_preview = ft.Container(
        width=60,
        height=60,
        bgcolor=app.cfg.get("accent", "#40C4FF"),
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=8, color=pal["shadow"]),
    )

    def save_click(_):
        from ankibot.config import save_config
        app.cfg["api_key"] = api_field.value.strip()
        save_config(app.cfg)
        app.backend = app.backend.__class__(app.cfg.get("api_key", ""), model=app.backend.cfg.model)
        app._apply_theme()
        app.page.appbar = build_appbar(app)
        app.content_area.content = build_settings(app)
        app.snack("✅ Paramètres enregistrés avec succès", pal["ok"])

    def reset_click(_):
        api_field.value = ""
        theme_dd.value = "system"
        accent_field.value = "#40C4FF"
        app.page.update()
        app.snack("🔄 Paramètres réinitialisés (non sauvegardés)", pal["warn"])

    save_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.SAVE_ROUNDED, size=20, color=ft.Colors.WHITE),
            ft.Text("Enregistrer", size=15, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=pal["ok"],
        padding=16,
        border_radius=12,
        ink=True,
        on_click=save_click,
        shadow=ft.BoxShadow(blur_radius=12, color=pal["ok"] + "40", offset=ft.Offset(0, 4)),
    )

    reset_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.RESTART_ALT_ROUNDED, size=18, color=pal["text"]),
            ft.Text("Réinitialiser", size=14, weight=ft.FontWeight.W_600, color=pal["text"]),
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor="transparent",
        padding=14,
        border_radius=12,
        border=ft.border.all(2, pal["border"]),
        ink=True,
        on_click=reset_click,
    )

    sidebar = _card(
        pal=pal,
        elevation=2,
        content=ft.Column([
            _section_header("Préférences", ft.Icons.SETTINGS_ROUNDED, pal),
            ft.Divider(color=pal["border"], height=20),
            theme_dd,
            ft.Container(height=4),
            ft.Row([
                ft.Container(content=accent_field, expand=True),
                color_preview,
            ], spacing=12, alignment=ft.MainAxisAlignment.START),
            ft.Container(height=4),
            api_field,
            ft.Container(
                content=ft.Text(
                    "💡 Obtenez votre clé API sur Google AI Studio",
                    size=12,
                    color=pal["muted"],
                    italic=True,
                ),
                padding=8,
                bgcolor=pal["surface_alt"],
                border_radius=8,
            ),
            ft.Container(height=12),
            save_btn,
            reset_btn,
        ], spacing=16),
    )
    sidebar.width = 400

    # Preview
    preview_card = ft.Container(
        bgcolor=pal["surface_alt"],
        padding=24,
        border_radius=16,
        border=ft.border.all(1, pal["border"]),
        shadow=ft.BoxShadow(blur_radius=16, color=pal["shadow"]),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.STYLE_ROUNDED, color=pal["accent"], size=24),
                ft.Text("Carte exemple", size=18, weight=ft.FontWeight.W_700, color=pal["text"]),
            ], spacing=12),
            ft.Divider(color=pal["border"], height=20),
            ft.Container(
                content=ft.Column([
                    ft.Text("Question:", size=12, color=pal["muted"], weight=ft.FontWeight.W_600),
                    ft.Text("Quelle est la capitale de la France?", size=15, color=pal["text"]),
                ], spacing=6),
                padding=16,
                bgcolor=pal["surface"],
                border_radius=12,
            ),
            ft.Container(height=8),
            ft.Container(
                content=ft.Column([
                    ft.Text("Réponse:", size=12, color=pal["muted"], weight=ft.FontWeight.W_600),
                    ft.Text("Paris", size=15, color=pal["accent"], weight=ft.FontWeight.W_700),
                ], spacing=6),
                padding=16,
                bgcolor=pal["surface"],
                border_radius=12,
            ),
        ], spacing=12),
    )

    workspace = _card(
        pal=pal,
        elevation=2,
        expand=True,
        content=ft.Column([
            _section_header("Aperçu en direct", ft.Icons.PREVIEW_ROUNDED, pal, "Visualisez le style de vos cartes"),
            ft.Divider(color=pal["border"], height=20),
            preview_card,
        ], spacing=16),
    )

    return ft.Column([
        ft.Row([sidebar, workspace], spacing=24, expand=True),
        build_status_bar(app),
    ], spacing=24, expand=True)