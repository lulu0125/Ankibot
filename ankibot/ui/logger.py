from __future__ import annotations
import flet as ft
import logging


class UILogHandler(logging.Handler):
    """Forward log records to the UI list via a callback."""
    def __init__(self, append_fn):
        super().__init__()
        self.append_fn = append_fn

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.append_fn(msg, record.levelno)
        except Exception:
            pass


def append_log(app, msg: str, levelno: int):
    if app.log_view is None:
        return
    pal = app._palette()
    color = pal["text"]
    if levelno >= logging.ERROR:
        color = pal["err"]
    elif levelno >= logging.WARNING:
        color = pal["warn"]
    elif levelno <= logging.INFO:
        color = pal["text"]
    app.log_view.controls.append(ft.Text(msg, size=13, color=color))
    app.log_view.auto_scroll = True
    app.page.update()


def snack(app, msg: str, color: str | None = None):
    pal = app._palette()
    sb = ft.SnackBar(
        content=ft.Text(msg, color="white"),
        bgcolor=color or pal["accent"],
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=3000,
        show_close_icon=True,
    )
    app.page.overlay.append(sb)
    sb.open = True
    app.page.update()
