from __future__ import annotations

import io
import csv
import flet as ft


def attach(app):
    # ---------------- Editable Cards Preview ---------------- #
    def _parse_cards_to_rows(csv_text: str):
        try:
            rows = list(csv.reader(io.StringIO(csv_text)))
            if not rows:
                rows = [["Topic","Subtopic","Question","Answer","Source","Details"]]
        except Exception:
            rows = [["Topic","Subtopic","Question","Answer","Source","Details"]]
        header = ["Topic","Subtopic","Question","Answer","Source","Details"]
        normalized = [header]
        for r in rows[1:]:
            padded = (r + [""] * 6)[:6]
            normalized.append(padded)
        app.card_rows = normalized

    def _refresh_cards_preview():
        if not app.cards_preview:
            return
        pal = app._palette()
        app.cards_preview.rows = []

        for idx, r in enumerate(app.card_rows[1:101], start=1):  # show max 100
            topic, subtopic, q, a, src, details = (r + [""] * 6)[:6]

            def make_edit_handler(row_index: int):
                def _(_e=None):
                    _open_edit_dialog(row_index)
                return _

            def make_delete_handler(row_index: int):
                def _(_e=None):
                    if 0 < row_index < len(app.card_rows):
                        del app.card_rows[row_index]
                        _refresh_cards_preview()
                        app.snack("Carte supprimée")
                return _

            edit_btn = ft.IconButton(icon=ft.Icons.EDIT, tooltip="Éditer", on_click=make_edit_handler(idx))
            del_btn = ft.IconButton(icon=ft.Icons.DELETE, tooltip="Supprimer", on_click=make_delete_handler(idx))

            app.cards_preview.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(topic[:40])),
                        ft.DataCell(ft.Text(subtopic[:40])),
                        ft.DataCell(ft.Text(q[:80])),
                        ft.DataCell(ft.Text(a[:80])),
                        ft.DataCell(ft.Text(src[:40])),
                        ft.DataCell(ft.Text(details[:60])),
                        ft.DataCell(edit_btn),
                        ft.DataCell(del_btn),
                    ]
                )
            )
        app.page.update()

    def _open_edit_dialog(row_index: int):
        if not (0 < row_index < len(app.card_rows)):
            return
        pal = app._palette()
        topic, subtopic, q, a, src, details = (app.card_rows[row_index] + [""] * 6)[:6]
        tf_topic = ft.TextField(label="Topic", value=topic, width=520)
        tf_subtopic = ft.TextField(label="Subtopic", value=subtopic, width=520)
        tf_q = ft.TextField(label="Question", value=q, width=520, multiline=True, min_lines=2, max_lines=3)
        tf_a = ft.TextField(label="Answer", value=a, width=520, multiline=True, min_lines=2, max_lines=4)
        tf_src = ft.TextField(label="Source", value=src, width=520)
        tf_det = ft.TextField(label="Details", value=details, width=520, multiline=True, min_lines=1, max_lines=3)

        def on_save(_):
            app.card_rows[row_index] = [tf_topic.value, tf_subtopic.value, tf_q.value, tf_a.value, tf_src.value, tf_det.value]
            dlg.open = False
            app.page.update()
            _refresh_cards_preview()
            app.snack("Carte mise à jour")

        def on_cancel(_):
            dlg.open = False
            app.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Éditer la carte"),
            content=ft.Column([tf_topic, tf_subtopic, tf_q, tf_a, tf_src, tf_det], tight=True, spacing=10, width=560),
            actions=[
                ft.TextButton("Annuler", on_click=on_cancel),
                ft.FilledButton("Enregistrer", on_click=on_save,
                                style=ft.ButtonStyle(bgcolor={"": pal["accent"], "hovered": pal["accent_hover"]}, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        app.page.open(dlg)
        app.page.update()

    # ---------------- Facts preview ---------------- #
    def _refresh_fact_preview():
        if not app.fact_preview:
            return
        rows = []
        for f in app.all_facts[:50]:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(f.topic or "")[:60])),
                        ft.DataCell(ft.Text(str(f.subtopic or "")[:60])),
                        ft.DataCell(ft.Text(str(f.fact or "")[:120])),
                        ft.DataCell(ft.Text(str(f.source or "")[:40])),
                    ]
                )
            )
        app.fact_preview.rows = rows
        app.page.update()

    # ---------------- Stats ---------------- #
    def _update_deck_stats():
        if not app.card_rows or len(app.card_rows) <= 1:
            if app.stats_badge:
                app.stats_badge.value = ""
                app.page.update()
            return
        data = app.card_rows[1:]
        total = len(data)
        counts: dict[str, int] = {}
        for r in data:
            topic = (r[0] if len(r) > 0 else "").strip() or "Untitled"
            counts[topic] = counts.get(topic, 0) + 1
        topics = len(counts)
        top_topic = max(counts, key=counts.get) if counts else "—"
        badge = f"🧮 {total} cartes • {topics} topics • Top: {top_topic} ({counts.get(top_topic, 0)})"
        if app.stats_badge:
            app.stats_badge.value = badge
        app.logger.info(badge)
        app.page.update()

    # bind
    app._parse_cards_to_rows = _parse_cards_to_rows
    app._refresh_cards_preview = _refresh_cards_preview
    app._open_edit_dialog = _open_edit_dialog
    app._refresh_fact_preview = _refresh_fact_preview
    app._update_deck_stats = _update_deck_stats
