from __future__ import annotations

import flet as ft

# =============================================================
# Ultra-Modern Dashboard UI for Ankibot
# - Premium design with glassmorphism and smooth animations
# - Step-by-step wizard flow with progress indicators
# - Proper scrolling and responsive layout
# - Enhanced empty states and loading experiences
# - Better information architecture
# =============================================================


# ---------------------------- Helpers ---------------------------- #

def _glassmorphic_card(
    content: ft.Control,
    *,
    pal: dict,
    padding: int = 24,
    radius: int = 20,
    expand: bool | int = False,
    blur: bool = False,
) -> ft.Container:
    """Premium glassmorphic card design."""
    return ft.Container(
        bgcolor=pal["surface"],
        border_radius=radius,
        padding=padding,
        border=ft.border.all(1, pal["border"]),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color=pal["shadow"],
            offset=ft.Offset(0, 8)
        ),
        content=content,
        expand=expand,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
    )


def _metric_card(icon: str, label: str, value: str, color: str, pal: dict) -> ft.Container:
    """Beautiful metric card for dashboard stats."""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=24, color=color),
                    bgcolor=color + "20",
                    padding=12,
                    border_radius=12,
                ),
                ft.Container(expand=True),
                ft.Text(value, size=28, weight=ft.FontWeight.W_800, color=pal["text"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(label, size=13, color=pal["muted"], weight=ft.FontWeight.W_500),
        ], spacing=12),
        bgcolor=pal["surface"],
        padding=20,
        border_radius=16,
        border=ft.border.all(1, pal["border"]),
        shadow=ft.BoxShadow(blur_radius=12, color=pal["shadow"], offset=ft.Offset(0, 4)),
    )


def _step_indicator(step: int, current: int, label: str, pal: dict) -> ft.Container:
    """Step indicator for wizard flow."""
    is_active = step == current
    is_complete = step < current
    
    if is_complete:
        icon = ft.Icons.CHECK_CIRCLE
        icon_color = pal["ok"]
        bg_color = pal["ok"] + "20"
    elif is_active:
        icon = ft.Icons.CIRCLE
        icon_color = pal["accent"]
        bg_color = pal["accent"] + "20"
    else:
        icon = ft.Icons.CIRCLE_OUTLINED
        icon_color = pal["muted"]
        bg_color = pal["surface_alt"]
    
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, size=32, color=icon_color),
            ft.Text(
                label,
                size=12,
                color=icon_color if (is_active or is_complete) else pal["muted"],
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400,
                text_align=ft.TextAlign.CENTER,
            ),
        ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=12,
        bgcolor=bg_color,
        border_radius=12,
        width=100,
    )


def _action_button(
    text: str,
    icon: str,
    color: str,
    *,
    on_click=None,
    outlined: bool = False,
    disabled: bool = False,
) -> ft.Container:
    """Premium action button with icon."""
    if outlined:
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=color if not disabled else "#888888"),
                ft.Text(
                    text,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=color if not disabled else "#888888"
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor="transparent",
            padding=ft.padding.symmetric(20, 14),
            border_radius=12,
            border=ft.border.all(2, color if not disabled else "#888888"),
            ink=not disabled,
            on_click=on_click if not disabled else None,
            opacity=0.5 if disabled else 1.0,
        )
    else:
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                ft.Text(text, size=15, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=color if not disabled else "#888888",
            padding=ft.padding.symmetric(20, 14),
            border_radius=12,
            ink=not disabled,
            on_click=on_click if not disabled else None,
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=color + "50" if not disabled else "#88888850",
                offset=ft.Offset(0, 6)
            ),
            opacity=0.7 if disabled else 1.0,
        )


def _empty_state(icon: str, title: str, subtitle: str, pal: dict, action_text: str = "", on_action=None) -> ft.Container:
    """Premium empty state with optional action."""
    items = [
        ft.Container(
            content=ft.Icon(icon, size=80, color=pal["muted"] + "30"),
            bgcolor=pal["surface_alt"],
            padding=24,
            border_radius=100,
        ),
        ft.Text(title, size=20, weight=ft.FontWeight.W_700, color=pal["text"]),
        ft.Text(
            subtitle,
            size=14,
            color=pal["muted"],
            text_align=ft.TextAlign.CENTER,
            max_lines=3,
        ),
    ]
    
    if action_text and on_action:
        items.append(
            ft.Container(
                content=ft.Text(action_text, size=14, weight=ft.FontWeight.W_600, color=pal["accent"]),
                padding=ft.padding.symmetric(16, 10),
                border_radius=8,
                border=ft.border.all(2, pal["accent"]),
                ink=True,
                on_click=on_action,
            )
        )
    
    return ft.Container(
        content=ft.Column(
            items,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=60,
        alignment=ft.alignment.center,
        expand=True,
    )


# ------------------------- Top App Bar ------------------------- #

def build_appbar(app) -> ft.AppBar:
    pal = app._palette()
    
    return ft.AppBar(
        leading=ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("⚡", size=24),
                    bgcolor=pal["accent"] + "20",
                    padding=8,
                    border_radius=10,
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.only(left=12),
        ),
        leading_width=60,
        title=ft.Text(
            "Ankibot", 
            size=22, 
            weight=ft.FontWeight.W_800,
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
                            shape=ft.RoundedRectangleBorder(radius=10),
                            bgcolor={ft.ControlState.HOVERED: pal["accent"] + "15"},
                        ),
                        on_click=lambda e: app._fade_to(build_home(app)),
                    ),
                    ft.IconButton(
                        ft.Icons.SETTINGS_ROUNDED,
                        tooltip="Paramètres",
                        icon_color=pal["text"],
                        icon_size=22,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            bgcolor={ft.ControlState.HOVERED: pal["accent"] + "15"},
                        ),
                        on_click=lambda e: app._fade_to(build_settings(app)),
                    ),
                    ft.Container(
                        content=ft.VerticalDivider(width=1, color=pal["border"]),
                        height=30,
                    ),
                    ft.IconButton(
                        ft.Icons.DARK_MODE_ROUNDED if app._is_dark() else ft.Icons.LIGHT_MODE_ROUNDED,
                        tooltip="Basculer thème",
                        icon_color=pal["accent"],
                        icon_size=22,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            bgcolor={ft.ControlState.HOVERED: pal["accent"] + "15"},
                        ),
                        on_click=app._toggle_theme,
                    ),
                ], spacing=6),
                padding=ft.padding.only(right=8),
            ),
        ],
    )


# ------------------------- Status Bar ------------------------- #

def build_status_bar(app) -> ft.Control:
    pal = app._palette()

    app.file_status = ft.Text("Aucun", size=13, color=pal["text"], weight=ft.FontWeight.W_600)
    api_connected = bool(app.cfg.get("api_key"))
    app.api_status = ft.Text(
        "Connectée" if api_connected else "Non configurée",
        color=pal["ok"] if api_connected else pal["err"],
        size=13,
        weight=ft.FontWeight.W_700,
    )
    app.stats_badge = ft.Text("—", size=13, color=pal["text"], weight=ft.FontWeight.W_600)

    return ft.Container(
        content=ft.Row([
            # Files
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=18, color=pal["accent"]),
                    ft.Column([
                        ft.Text("Fichiers", size=11, color=pal["muted"]),
                        app.file_status,
                    ], spacing=2),
                ], spacing=12),
                padding=16,
                bgcolor=pal["surface_alt"],
                border_radius=12,
                expand=True,
            ),
            # Stats
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.AUTO_GRAPH_ROUNDED, size=18, color=pal["info"]),
                    ft.Column([
                        ft.Text("Résultats", size=11, color=pal["muted"]),
                        app.stats_badge,
                    ], spacing=2),
                ], spacing=12),
                padding=16,
                bgcolor=pal["surface_alt"],
                border_radius=12,
                expand=True,
            ),
            # API
            ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.API_ROUNDED,
                        size=18,
                        color=pal["ok"] if api_connected else pal["err"]
                    ),
                    ft.Column([
                        ft.Text("API Status", size=11, color=pal["muted"]),
                        app.api_status,
                    ], spacing=2),
                ], spacing=12),
                padding=16,
                bgcolor=pal["surface_alt"],
                border_radius=12,
                expand=True,
            ),
        ], spacing=12),
        padding=0,
    )


# --------------------------- Home --------------------------- #

def build_home(app) -> ft.Control:
    pal = app._palette()

    # ----- Hero Section ----- #
    hero = _glassmorphic_card(
        pal=pal,
        radius=24,
        padding=32,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text("⚡", size=42),
                        ft.Column([
                            ft.Text("Ankibot", size=36, weight=ft.FontWeight.W_900, color=pal["text"]),
                            ft.Container(
                                content=ft.Text(
                                    "Powered by Gemini AI",
                                    size=12,
                                    color=pal["accent"],
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=pal["accent"] + "15",
                                padding=ft.padding.symmetric(8, 4),
                                border_radius=6,
                            ),
                        ], spacing=4),
                    ], spacing=16, alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=8),
                    ft.Text(
                        "Transformez vos documents en flashcards Anki intelligemment",
                        size=16,
                        color=pal["text_secondary"],
                        weight=ft.FontWeight.W_500,
                    ),
                ], spacing=4, expand=True),
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.AUTO_AWESOME_ROUNDED,
                        size=64,
                        color=pal["accent"] + "60"
                    ),
                    bgcolor=pal["accent"] + "15",
                    padding=20,
                    border_radius=20,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], spacing=0),
    )

    # ----- Configuration Section ----- #
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
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        on_change=app._on_model_change,
    )

    density_label = ft.Text("Normal", size=14, color=pal["accent"], weight=ft.FontWeight.W_700)
    density_desc = {
        1: ("Sparse", "Moins de cartes, concepts essentiels"),
        2: ("Normal", "Équilibre optimal"),
        3: ("Dense", "Maximum de détails"),
    }
    density_subtitle = ft.Text(
        density_desc[app.density_level][1],
        size=12,
        color=pal["muted"],
        italic=True,
    )

    def update_density_desc(e):
        level = int(e.control.value)
        density_label.value = density_desc[level][0]
        density_subtitle.value = density_desc[level][1]
        app._update_density(e, density_label)

    density_slider = ft.Slider(
        min=1,
        max=3,
        divisions=2,
        value=app.density_level,
        active_color=pal["accent"],
        inactive_color=pal["border"],
        thumb_color=pal["accent"],
        on_change=update_density_desc,
    )

    config_section = _glassmorphic_card(
        pal=pal,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.TUNE_ROUNDED, color=pal["accent"], size=22),
                ft.Text("Configuration", size=18, weight=ft.FontWeight.W_700, color=pal["text"]),
            ], spacing=12),
            ft.Divider(color=pal["border"], height=20),
            model_dd,
            ft.Container(height=8),
            ft.Row([
                ft.Column([
                    ft.Text("Densité des cartes", size=14, color=pal["text"], weight=ft.FontWeight.W_600),
                    density_subtitle,
                ], spacing=4, expand=True),
                density_label,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            density_slider,
            ft.Container(height=8),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TUNE, size=16, color=pal["muted"]),
                        ft.Text("Options avancées", size=13, color=pal["muted"], weight=ft.FontWeight.W_600),
                    ], spacing=8),
                    ft.Divider(color=pal["border"], height=12),
                    ft.Switch(
                        label="Cartes inversées (question ↔ réponse)",
                        value=app.reverse_card,
                        active_color=pal["accent"],
                        label_style=ft.TextStyle(size=13, color=pal["text"]),
                        on_change=lambda e: setattr(app, "reverse_card", e.control.value),
                    ),
                    ft.Switch(
                        label="Séparer les decks par topic",
                        value=app.split_by_topic,
                        active_color=pal["accent"],
                        label_style=ft.TextStyle(size=13, color=pal["text"]),
                        on_change=lambda e: setattr(app, "split_by_topic", e.control.value),
                    ),
                    ft.Switch(
                        label="Double vérification (plus lent mais précis)",
                        value=app.double_check,
                        active_color=pal["accent"],
                        label_style=ft.TextStyle(size=13, color=pal["text"]),
                        on_change=lambda e: setattr(app, "double_check", e.control.value),
                    ),
                    ft.Switch(
                        label="Nouveau pipeline expérimental",
                        value=app.new_pipeline,
                        active_color=pal["accent"],
                        label_style=ft.TextStyle(size=13, color=pal["text"]),
                        on_change=lambda e: setattr(app, "new_pipeline", e.control.value),
                    ),
                ], spacing=10),
                padding=16,
                bgcolor=pal["surface_alt"],
                border_radius=12,
                border=ft.border.all(1, pal["border"]),
            ),
        ], spacing=16),
    )

    # ----- Input Section ----- #
    fp = ft.FilePicker(on_result=app._on_pick)
    app.page.overlay.append(fp)

    input_section = _glassmorphic_card(
        pal=pal,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INPUT_ROUNDED, color=pal["info"], size=22),
                ft.Text("Source du contenu", size=18, weight=ft.FontWeight.W_700, color=pal["text"]),
            ], spacing=12),
            ft.Divider(color=pal["border"], height=20),
            
            # File upload area
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CLOUD_UPLOAD_ROUNDED, size=48, color=pal["accent"] + "60"),
                    ft.Text(
                        "Glissez vos fichiers ici ou cliquez pour parcourir",
                        size=15,
                        color=pal["text"],
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        "PDF et TXT supportés • Plusieurs fichiers possibles",
                        size=12,
                        color=pal["muted"],
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=18, color=pal["accent"]),
                            ft.Text("Parcourir les fichiers", size=14, weight=ft.FontWeight.W_600, color=pal["accent"]),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                        padding=ft.padding.symmetric(20, 12),
                        bgcolor=pal["accent"] + "15",
                        border_radius=10,
                        border=ft.border.all(2, pal["accent"] + "40"),
                        ink=True,
                        on_click=lambda e: fp.pick_files(allow_multiple=True, allowed_extensions=["pdf", "txt"]),
                    ),
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=pal["surface_alt"],
                border_radius=12,
                border=ft.border.all(2, pal["border"]),
            ),
            
            ft.Row([
                ft.Container(expand=True, height=1, bgcolor=pal["border"]),
                ft.Text("OU", size=12, color=pal["muted"], weight=ft.FontWeight.W_600),
                ft.Container(expand=True, height=1, bgcolor=pal["border"]),
            ], spacing=12),
            
            # Text input
            ft.TextField(
                label="📝 Collez votre texte directement",
                multiline=True,
                min_lines=5,
                max_lines=10,
                border_radius=12,
                text_style=ft.TextStyle(color=pal["text"], size=14),
                bgcolor=pal["surface_alt"],
                hint_text="Collez le contenu de vos cours ici...",
                border_color=pal["border"],
                focused_border_color=pal["info"],
                ref=ft.Ref[ft.TextField](),  # Store reference
            ),
            
            # Custom rules
            ft.TextField(
                label="✨ Instructions personnalisées (optionnel)",
                multiline=True,
                min_lines=2,
                max_lines=4,
                border_radius=12,
                text_style=ft.TextStyle(color=pal["text"], size=14),
                bgcolor=pal["surface_alt"],
                hint_text="Ex: Insister sur les dates historiques, créer des questions de type QCM...",
                border_color=pal["border"],
                focused_border_color=pal["info"],
                on_change=lambda e: setattr(app, "custom_add", e.control.value),
            ),
        ], spacing=16),
    )

    # Store text field reference
    text_area_ref = input_section.content.controls[4]

    # ----- Action Section ----- #
    app.progress = ft.ProgressBar(
        color=pal["accent"],
        bgcolor=pal["border"],
        height=8,
        border_radius=4,
        visible=False,
    )
    app.progress_label = ft.Text(
        "",
        color=pal["text"],
        size=13,
        weight=ft.FontWeight.W_600,
        text_align=ft.TextAlign.CENTER,
    )

    action_section = _glassmorphic_card(
        pal=pal,
        content=ft.Column([
            ft.Row([
                _action_button(
                    "✨ Générer les flashcards",
                    ft.Icons.AUTO_AWESOME_ROUNDED,
                    pal["accent"],
                    on_click=lambda e: app.page.run_task(
                        app._start_pipeline,
                        text_area_ref.value if hasattr(text_area_ref, 'value') else ""
                    ),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            app.progress,
            app.progress_label,
            ft.Container(height=8),
            ft.Row([
                _action_button(
                    "Annuler",
                    ft.Icons.CANCEL_ROUNDED,
                    pal["err"],
                    outlined=True,
                    on_click=lambda e: app.cancel_event.set(),
                ),
                _action_button(
                    "Exporter",
                    ft.Icons.DOWNLOAD_ROUNDED,
                    pal["ok"],
                    outlined=True,
                    on_click=lambda e: app.page.run_task(app._save_outputs),
                ),
            ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

# ----- Results Section ----- #
    
    # Initialize data containers
    app.log_view = ft.ListView(expand=True, spacing=8, auto_scroll=True, padding=20)
    
    # Stats summary for each tab
    app.facts_stats = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=16, color=pal["muted"]),
            ft.Text("0 faits • 0 topics", size=12, color=pal["muted"], weight=ft.FontWeight.W_600),
        ], spacing=8),
        padding=ft.padding.symmetric(12, 8),
        bgcolor=pal["surface_alt"],
        border_radius=8,
        visible=False,
    )
    
    app.cards_stats = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=16, color=pal["muted"]),
            ft.Text("0 cartes • 0 topics", size=12, color=pal["muted"], weight=ft.FontWeight.W_600),
        ], spacing=8),
        padding=ft.padding.symmetric(12, 8),
        bgcolor=pal["surface_alt"],
        border_radius=8,
        visible=False,
    )
    
    # Search and filter controls
    app.search_facts = ft.TextField(
        hint_text="🔍 Rechercher dans les faits...",
        border_radius=10,
        text_style=ft.TextStyle(size=13, color=pal["text"]),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        height=40,
        content_padding=ft.padding.symmetric(12, 8),
        visible=False,
    )
    
    app.search_cards = ft.TextField(
        hint_text="🔍 Rechercher dans les cartes...",
        border_radius=10,
        text_style=ft.TextStyle(size=13, color=pal["text"]),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        height=40,
        content_padding=ft.padding.symmetric(12, 8),
        visible=False,
    )
    
    # Enhanced data tables with better styling
    app.fact_preview = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Topic", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Subtopic", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Fact", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Source", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
        ],
        rows=[],
        border=ft.border.all(1, pal["border"]),
        border_radius=12,
        heading_row_color=pal["surface_alt"],
        heading_row_height=48,
        data_row_min_height=70,
        data_row_max_height=120,
        column_spacing=24,
        horizontal_lines=ft.BorderSide(1, pal["border"] + "40"),
        show_checkbox_column=False,
    )

    app.cards_preview = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Topic", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Subtopic", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Question", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Réponse", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Source", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Text("Détails", weight=ft.FontWeight.W_700, size=13, color=pal["text"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT_ROUNDED, size=18, color=pal["accent"]),
                    padding=8,
                )
            ),
            ft.DataColumn(
                ft.Container(
                    content=ft.Icon(ft.Icons.DELETE_ROUNDED, size=18, color=pal["err"]),
                    padding=8,
                )
            ),
        ],
        rows=[],
        border=ft.border.all(1, pal["border"]),
        border_radius=12,
        heading_row_color=pal["surface_alt"],
        heading_row_height=48,
        data_row_min_height=80,
        data_row_max_height=150,
        column_spacing=16,
        horizontal_lines=ft.BorderSide(1, pal["border"] + "40"),
        show_checkbox_column=False,
    )

    # Enhanced empty states with animations
    facts_empty = _empty_state(
        ft.Icons.LIGHTBULB_OUTLINE_ROUNDED,
        "Aucun fait extrait",
        "Les faits importants seront extraits de vos documents\net organisés par topic et subtopic",
        pal,
        action_text="📚 Comment ça marche ?",
        on_action=lambda e: app.snack("Les faits sont extraits automatiquement lors du traitement", pal["info"])
    )

    cards_empty = _empty_state(
        ft.Icons.STYLE_ROUNDED,
        "Aucune carte générée",
        "Les flashcards intelligentes seront créées à partir\ndes faits extraits avec questions contextuelles",
        pal,
        action_text="✨ Voir un exemple",
        on_action=lambda e: app._fade_to(build_settings(app))
    )

    logs_empty = _empty_state(
        ft.Icons.TERMINAL_ROUNDED,
        "En attente de traitement",
        "Les logs de génération apparaîtront ici en temps réel\npour suivre la progression du pipeline",
        pal
    )

    # Tabs with improved design
    app.preview_tab = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        label_color=pal["accent"],
        indicator_color=pal["accent"],
        indicator_tab_size=True,
        indicator_border_radius=ft.border_radius.only(top_left=8, top_right=8),
        divider_color=pal["border"],
        overlay_color={ft.ControlState.HOVERED: pal["accent"] + "10"},
        tabs=[
            ft.Tab(
                text="Faits extraits",
                icon=ft.Icons.LIGHTBULB_ROUNDED,
            ),
            ft.Tab(
                text="Flashcards",
                icon=ft.Icons.STYLE_ROUNDED,
            ),
            ft.Tab(
                text="Logs",
                icon=ft.Icons.TERMINAL_ROUNDED,
            ),
        ],
    )

    # Content containers with proper state management
    facts_content = ft.Column([
        ft.Row([
            app.search_facts,
            app.facts_stats,
        ], spacing=12),
        ft.Container(height=8),
        facts_empty,
    ], expand=True, spacing=0)
    
    cards_content = ft.Column([
        ft.Row([
            app.search_cards,
            app.cards_stats,
        ], spacing=12),
        ft.Container(height=8),
        cards_empty,
    ], expand=True, spacing=0)
    
    logs_content = ft.Column([
        logs_empty,
    ], expand=True, spacing=0)

    # Main content stack with smooth transitions
    fact_scroll = ft.Container(
        content=facts_content,
        visible=True,
        expand=True,
        padding=20,
        animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
    )

    cards_scroll = ft.Container(
        content=cards_content,
        visible=False,
        expand=True,
        padding=20,
        animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
    )

    logs_scroll = ft.Container(
        content=logs_content,
        visible=False,
        expand=True,
        animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
    )

    def update_facts_view():
        """Update facts view with current data."""
        has_facts = len(app.fact_preview.rows) > 0
        
        if has_facts:
            # Count unique topics
            topics = set()
            for row in app.fact_preview.rows:
                if row.cells and len(row.cells) > 0:
                    topics.add(str(row.cells[0].content.value))
            
            # Update stats
            app.facts_stats.content.controls[1].value = f"{len(app.fact_preview.rows)} faits • {len(topics)} topics"
            app.facts_stats.visible = True
            app.search_facts.visible = len(app.fact_preview.rows) > 5
            
            # Show table
            facts_content.controls = [
                ft.Row([app.search_facts, app.facts_stats], spacing=12),
                ft.Container(height=12),
                ft.Column([
                    ft.Row([app.fact_preview], scroll=ft.ScrollMode.AUTO),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
            ]
        else:
            app.facts_stats.visible = False
            app.search_facts.visible = False
            facts_content.controls = [facts_empty]
        
        app.page.update()
    
    def update_cards_view():
        """Update cards view with current data."""
        has_cards = len(app.cards_preview.rows) > 0
        
        if has_cards:
            # Count unique topics
            topics = set()
            for row in app.cards_preview.rows:
                if row.cells and len(row.cells) > 0:
                    topics.add(str(row.cells[0].content.value))
            
            # Update stats
            app.cards_stats.content.controls[1].value = f"{len(app.cards_preview.rows)} cartes • {len(topics)} topics"
            app.cards_stats.visible = True
            app.search_cards.visible = len(app.cards_preview.rows) > 5
            
            # Show table
            cards_content.controls = [
                ft.Row([app.search_cards, app.cards_stats], spacing=12),
                ft.Container(height=12),
                ft.Column([
                    ft.Row([app.cards_preview], scroll=ft.ScrollMode.AUTO),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
            ]
        else:
            app.cards_stats.visible = False
            app.search_cards.visible = False
            cards_content.controls = [cards_empty]
        
        app.page.update()
    
    def update_logs_view():
        """Update logs view with current data."""
        has_logs = len(app.log_view.controls) > 0
        
        if has_logs:
            logs_content.controls = [app.log_view]
        else:
            logs_content.controls = [logs_empty]
        
        app.page.update()

    def on_tab_change(_e: ft.ControlEvent):
        """Handle tab changes with smooth transitions - SANS reconstruire."""
        idx = app.preview_tab.selected_index
        
        # Hide all
        fact_scroll.visible = False
        cards_scroll.visible = False
        logs_scroll.visible = False
        
        # Show selected and update content
        if idx == 0:
            fact_scroll.visible = True
            update_facts_view()
        elif idx == 1:
            cards_scroll.visible = True
            update_cards_view()
        elif idx == 2:
            logs_scroll.visible = True
            update_logs_view()
        
        # ✅ Update uniquement les containers concernés
        try:
            fact_scroll.update()
            cards_scroll.update()
            logs_scroll.update()
        except:
            # Fallback si update() n'est pas disponible
            app.page.update()

    app.preview_tab.on_change = on_tab_change
    
    # Store update functions for external use
    app.update_facts_view = update_facts_view
    app.update_cards_view = update_cards_view
    app.update_logs_view = update_logs_view

    # Action toolbar
    action_toolbar = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.VISIBILITY_ROUNDED, color=pal["accent"], size=22),
            ft.Text("Résultats", size=18, weight=ft.FontWeight.W_700, color=pal["text"]),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=16, color=pal["info"]),
                    ft.Text(
                        "Double-cliquez ✏️ pour éditer • Cliquez 🗑️ pour supprimer",
                        size=11,
                        color=pal["muted"],
                        weight=ft.FontWeight.W_500,
                    ),
                ], spacing=6),
                padding=ft.padding.symmetric(12, 8),
                bgcolor=pal["info"] + "10",
                border_radius=8,
                border=ft.border.all(1, pal["info"] + "20"),
            ),
        ], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.only(bottom=16),
    )

    results_section = _glassmorphic_card(
        pal=pal,
        expand=True,
        content=ft.Column([
            action_toolbar,
            ft.Divider(color=pal["border"], height=1),
            ft.Container(height=8),
            app.preview_tab,
            ft.Container(height=8),
            ft.Stack([
                fact_scroll,
                cards_scroll,
                logs_scroll,
            ], expand=True),
        ], spacing=0, expand=True, height=800, auto_scroll=False),
    )

    # ----- Main Layout ----- #
    left_column = ft.Column([
        config_section,
        input_section,
        action_section,
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    right_column = ft.Column([
        results_section,
    ], spacing=20, expand=True)

    main_content = ft.Row([
        ft.Container(content=left_column, width=480),
        ft.Container(content=right_column, expand=True),
    ], spacing=24, expand=True, alignment=ft.MainAxisAlignment.START)

    # Final layout with proper scrolling
    return ft.Column([
        hero,
        ft.Container(
            content=main_content,
            expand=True,
        ),
        build_status_bar(app),
    ], spacing=24, expand=True, scroll=ft.ScrollMode.AUTO)


# -------------------------- Settings -------------------------- #

def build_settings(app) -> ft.Control:
    pal = app._palette()

    # ----- Preferences ----- #
    api_field = ft.TextField(
        label="🔑 Clé API Google Gemini",
        value=app.cfg.get("api_key", ""),
        password=True,
        can_reveal_password=True,
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        hint_text="Entrez votre clé API...",
    )

    theme_dd = ft.Dropdown(
        label="🎨 Thème de l'interface",
        options=[
            ft.dropdown.Option("system", "🖥️  Automatique (système)"),
            ft.dropdown.Option("light", "☀️  Clair"),
            ft.dropdown.Option("dark", "🌙  Sombre"),
        ],
        value=app.cfg.get("theme", "system"),
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        on_change=lambda e: app._set_theme(e.control.value),
    )

    # Color picker with live preview
    accent_field = ft.TextField(
        label="🎨 Couleur d'accent (hex)",
        value=app.cfg.get("accent", "#40C4FF"),
        border_radius=12,
        text_style=ft.TextStyle(color=pal["text"], size=14),
        bgcolor=pal["surface_alt"],
        border_color=pal["border"],
        focused_border_color=pal["accent"],
        hint_text="#40C4FF",
        on_change=lambda e: app._set_accent(e.control.value),
    )

    color_preview = ft.Container(
        width=80,
        height=80,
        bgcolor=app.cfg.get("accent", "#40C4FF"),
        border_radius=16,
        border=ft.border.all(3, pal["border"]),
        shadow=ft.BoxShadow(blur_radius=16, color=pal["shadow"]),
    )

    def save_click(_):
        from ankibot.config import save_config
        app.cfg["api_key"] = api_field.value.strip()
        save_config(app.cfg)
        app.backend = app.backend.__class__(app.cfg.get("api_key", ""), model=app.backend.cfg.model)
        app._apply_theme()
        app.page.appbar = build_appbar(app)
        app.content_area.content = build_settings(app)
        app.snack("✅ Paramètres sauvegardés avec succès", pal["ok"])

    def reset_click(_):
        api_field.value = ""
        theme_dd.value = "system"
        accent_field.value = "#40C4FF"
        color_preview.bgcolor = "#40C4FF"
        app.page.update()
        app.snack("🔄 Réinitialisation effectuée", pal["warn"])

    preferences = _glassmorphic_card(
        pal=pal,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=pal["accent"], size=24),
                ft.Text("Préférences", size=20, weight=ft.FontWeight.W_800, color=pal["text"]),
            ], spacing=12),
            ft.Divider(color=pal["border"], height=24),
            
            theme_dd,
            ft.Container(height=8),
            
            ft.Text("Couleur d'accent", size=14, weight=ft.FontWeight.W_600, color=pal["text"]),
            ft.Row([
                ft.Container(content=accent_field, expand=True),
                color_preview,
            ], spacing=16),
            
            ft.Container(height=8),
            api_field,
            
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=16, color=pal["info"]),
                    ft.Text(
                        "Obtenez votre clé sur aistudio.google.com",
                        size=12,
                        color=pal["text_secondary"],
                        weight=ft.FontWeight.W_500,
                    ),
                ], spacing=8),
                padding=12,
                bgcolor=pal["info"] + "15",
                border_radius=10,
                border=ft.border.all(1, pal["info"] + "30"),
            ),
            
            ft.Container(height=16),
            
            ft.Row([
                _action_button(
                    "💾 Enregistrer",
                    ft.Icons.SAVE_ROUNDED,
                    pal["ok"],
                    on_click=save_click,
                ),
                _action_button(
                    "🔄 Réinitialiser",
                    ft.Icons.RESTART_ALT_ROUNDED,
                    pal["warn"],
                    outlined=True,
                    on_click=reset_click,
                ),
            ], spacing=12),
        ], spacing=16),
    )

    # ----- Live Preview ----- #
    preview = _glassmorphic_card(
        pal=pal,
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PREVIEW_ROUNDED, color=pal["info"], size=24),
                ft.Text("Aperçu en direct", size=20, weight=ft.FontWeight.W_800, color=pal["text"]),
            ], spacing=12),
            ft.Divider(color=pal["border"], height=24),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.STYLE_ROUNDED, color=pal["accent"], size=28),
                            bgcolor=pal["accent"] + "20",
                            padding=14,
                            border_radius=12,
                        ),
                        ft.Column([
                            ft.Text("Exemple de Flashcard", size=16, weight=ft.FontWeight.W_700, color=pal["text"]),
                            ft.Text("Topic: Histoire • Subtopic: Révolution", size=12, color=pal["muted"]),
                        ], spacing=4, expand=True),
                    ], spacing=16),
                    
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.HELP_OUTLINE_ROUNDED, size=18, color=pal["text_secondary"]),
                                ft.Text("Question", size=12, color=pal["text_secondary"], weight=ft.FontWeight.W_700),
                            ], spacing=8),
                            ft.Text(
                                "Quelle est la date de la prise de la Bastille?",
                                size=15,
                                color=pal["text"],
                                weight=ft.FontWeight.W_500,
                            ),
                        ], spacing=8),
                        padding=20,
                        bgcolor=pal["surface_alt"],
                        border_radius=12,
                        border=ft.border.all(1, pal["border"]),
                    ),
                    
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=18, color=pal["accent"]),
                                ft.Text("Réponse", size=12, color=pal["accent"], weight=ft.FontWeight.W_700),
                            ], spacing=8),
                            ft.Text(
                                "14 juillet 1789",
                                size=16,
                                color=pal["accent"],
                                weight=ft.FontWeight.W_700,
                            ),
                        ], spacing=8),
                        padding=20,
                        bgcolor=pal["accent"] + "10",
                        border_radius=12,
                        border=ft.border.all(2, pal["accent"] + "40"),
                    ),
                    
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📚 Source: Cours d'histoire - Chapitre 3", size=11, color=pal["muted"]),
                            ft.Text("💡 Détails: Événement marquant le début de la Révolution française", size=11, color=pal["muted"]),
                        ], spacing=6),
                        padding=16,
                        bgcolor=pal["surface_alt"],
                        border_radius=10,
                    ),
                ], spacing=0),
                padding=24,
                bgcolor=pal["surface"],
                border_radius=16,
                border=ft.border.all(1, pal["border"]),
                shadow=ft.BoxShadow(blur_radius=20, color=pal["shadow"]),
            ),
        ], spacing=16, expand=True),
    )

    # ----- Layout ----- #
    content = ft.Row([
        ft.Container(content=preferences, width=450),
        ft.Container(content=preview, expand=True),
    ], spacing=24, expand=True)

    return ft.Column([
        content,
        build_status_bar(app),
    ], spacing=24, expand=True, scroll=ft.ScrollMode.AUTO)