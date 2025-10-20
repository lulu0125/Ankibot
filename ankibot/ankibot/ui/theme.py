from __future__ import annotations
import flet as ft
from ankibot.utils import with_opacity


def is_dark(app) -> bool:
    """Determine if dark mode is active."""
    mode = app.cfg.get("theme", "system")
    if mode == "dark":
        return True
    if mode == "light":
        return False
    return str(app.page.platform_brightness).lower() == "dark"


def palette(app) -> dict[str, str]:
    """
    Enhanced color palette with better contrast and modern aesthetics.
    Returns a complete set of semantic colors for the UI.
    """
    accent = app.cfg.get("accent", "#40C4FF")
    dark = is_dark(app)
    
    if dark:
        return {
            # Backgrounds
            "bg": "#0A0E12",                    # Deep dark background
            "surface": "#151B23",               # Card surface
            "surface_alt": "#1E252E",           # Alternative surface (slightly lighter)
            
            # Text colors
            "text": "#F1F3F5",                  # Primary text - high contrast
            "text_secondary": "#B4BCC6",        # Secondary text
            "muted": "#8A95A3",                 # Muted/disabled text
            
            # UI Elements
            "border": "#2A3441",                # Borders and dividers
            "shadow": "#00000055",              # Shadows (with opacity)
            
            # Accent and semantic colors
            "accent": accent,
            "accent_hover": with_opacity(0.85, accent),
            "accent_light": accent + "30",      # Translucent accent
            
            # Status colors
            "ok": "#4ADE80",                    # Success/OK green
            "ok_light": "#4ADE8030",
            "warn": "#FBBF24",                  # Warning yellow
            "warn_light": "#FBBF2430",
            "err": "#F87171",                   # Error red
            "err_light": "#F8717130",
            "info": "#60A5FA",                  # Info blue
            "info_light": "#60A5FA30",
            
            # Interactive states
            "hover": "#252D38",
            "active": "#2A3441",
            "chip": "#232A35",
        }
    else:
        return {
            # Backgrounds
            "bg": "#F8FAFC",                    # Soft light background
            "surface": "#FFFFFF",               # Pure white cards
            "surface_alt": "#F1F5F9",           # Subtle alternative surface
            
            # Text colors
            "text": "#0F172A",                  # Dark text - high contrast
            "text_secondary": "#475569",        # Secondary text
            "muted": "#94A3B8",                 # Muted/disabled text
            
            # UI Elements
            "border": "#E2E8F0",                # Light borders
            "shadow": "#0000000D",              # Subtle shadows
            
            # Accent and semantic colors
            "accent": accent,
            "accent_hover": with_opacity(0.85, accent),
            "accent_light": accent + "15",
            
            # Status colors
            "ok": "#16A34A",                    # Success green
            "ok_light": "#16A34A15",
            "warn": "#F59E0B",                  # Warning orange
            "warn_light": "#F59E0B15",
            "err": "#DC2626",                   # Error red
            "err_light": "#DC262615",
            "info": "#2563EB",                  # Info blue
            "info_light": "#2563EB15",
            
            # Interactive states
            "hover": "#F8FAFC",
            "active": "#F1F5F9",
            "chip": "#F1F5F9",
        }


def apply_theme(app):
    """
    Apply the complete theme to the application.
    Sets colors, fonts, and Material 3 design tokens.
    """
    pal = palette(app)
    mode = app.cfg.get("theme", "system")
    
    # Set theme mode
    if mode == "dark":
        app.page.theme_mode = ft.ThemeMode.DARK
    elif mode == "light":
        app.page.theme_mode = ft.ThemeMode.LIGHT
    else:
        app.page.theme_mode = ft.ThemeMode.SYSTEM
    
    # Create enhanced Material 3 theme
    app.page.theme = ft.Theme(
        color_scheme_seed=pal["accent"],
        use_material3=True,
        visual_density=ft.VisualDensity.STANDARD,
        # Custom color scheme
        color_scheme=ft.ColorScheme(
            primary=pal["accent"],
            on_primary=ft.Colors.WHITE,
            surface=pal["surface"],
            on_surface=pal["text"],
            background=pal["bg"],
            on_background=pal["text"],
        ),
        # Typography
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(
                size=32,
                weight=ft.FontWeight.W_800,
                color=pal["text"],
            ),
            headline_large=ft.TextStyle(
                size=24,
                weight=ft.FontWeight.W_700,
                color=pal["text"],
            ),
            headline_medium=ft.TextStyle(
                size=20,
                weight=ft.FontWeight.W_600,
                color=pal["text"],
            ),
            title_large=ft.TextStyle(
                size=18,
                weight=ft.FontWeight.W_600,
                color=pal["text"],
            ),
            body_large=ft.TextStyle(
                size=15,
                weight=ft.FontWeight.W_400,
                color=pal["text"],
            ),
            body_medium=ft.TextStyle(
                size=14,
                weight=ft.FontWeight.W_400,
                color=pal["text_secondary"],
            ),
            label_large=ft.TextStyle(
                size=13,
                weight=ft.FontWeight.W_500,
                color=pal["text"],
            ),
        ),
    )
    
    # Set page background
    app.page.bgcolor = pal["bg"]
    
    # Smooth transitions
    app.page.theme.page_transitions = ft.PageTransitionsTheme(
        android=ft.PageTransitionTheme.OPEN_UPWARDS,
        ios=ft.PageTransitionTheme.CUPERTINO,
        macos=ft.PageTransitionTheme.FADE_UPWARDS,
        linux=ft.PageTransitionTheme.FADE_UPWARDS,
        windows=ft.PageTransitionTheme.OPEN_UPWARDS,
    )


def get_semantic_color(app, semantic: str) -> str:
    """
    Get a semantic color from the palette.
    
    Args:
        app: Application instance
        semantic: Color semantic key (e.g., 'ok', 'warn', 'err', 'info')
    
    Returns:
        Color hex string
    """
    pal = palette(app)
    return pal.get(semantic, pal["accent"])


def create_gradient(color1: str, color2: str, angle: int = 135) -> ft.LinearGradient:
    """
    Create a linear gradient between two colors.
    
    Args:
        color1: Start color (hex)
        color2: End color (hex)
        angle: Gradient angle in degrees (default: 135 = diagonal)
    
    Returns:
        LinearGradient object
    """
    # Convert angle to begin/end coordinates
    # 0° = left to right, 90° = top to bottom, etc.
    import math
    rad = math.radians(angle)
    
    return ft.LinearGradient(
        begin=ft.alignment.center_left,
        end=ft.alignment.center_right,
        colors=[color1, color2],
        rotation=angle,
    )


def apply_elevation(container: ft.Container, level: int, pal: dict) -> ft.Container:
    """
    Apply Material 3 elevation to a container.
    
    Args:
        container: Container to apply elevation to
        level: Elevation level (0-5)
        pal: Color palette
    
    Returns:
        Container with elevation applied
    """
    elevation_shadows = {
        0: None,
        1: ft.BoxShadow(blur_radius=4, spread_radius=0, color=pal["shadow"], offset=ft.Offset(0, 1)),
        2: ft.BoxShadow(blur_radius=8, spread_radius=0, color=pal["shadow"], offset=ft.Offset(0, 2)),
        3: ft.BoxShadow(blur_radius=12, spread_radius=0, color=pal["shadow"], offset=ft.Offset(0, 4)),
        4: ft.BoxShadow(blur_radius=16, spread_radius=0, color=pal["shadow"], offset=ft.Offset(0, 6)),
        5: ft.BoxShadow(blur_radius=24, spread_radius=0, color=pal["shadow"], offset=ft.Offset(0, 8)),
    }
    
    container.shadow = elevation_shadows.get(level, elevation_shadows[2])
    return container