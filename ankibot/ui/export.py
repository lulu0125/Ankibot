from __future__ import annotations
import os
import re
import io
import csv
import asyncio
import flet as ft


def attach(app):
    def _rows_to_csv_text() -> str:
        """Build CSV text from editable rows (ensuring header)."""
        if not app.card_rows:
            return ""
        out = io.StringIO()
        w = csv.writer(out, quoting=csv.QUOTE_ALL)
        header = ["Topic","Subtopic","Question","Answer","Source","Details"]
        w.writerow(header)
        for r in app.card_rows[1:]:
            w.writerow((r + [""] * 6)[:6])
        return out.getvalue()

    async def _save_outputs():
        pal = app._palette()
        csv_verified = _rows_to_csv_text()
        if not csv_verified.strip():
            csv_verified = app.verified_csv or app.generated_csv
        if not csv_verified.strip():
            app.snack("Aucun CSV à enregistrer", pal["err"])
            return

        base_name = "ankibot"
        if app.selected_files:
            if len(app.selected_files) == 1:
                base_name = os.path.splitext(os.path.basename(app.selected_files[0]))[0]
            else:
                base_name = os.path.commonprefix([os.path.basename(p) for p in app.selected_files]).strip("-_ ") or "ankibot"
        default_csv = f"{base_name}.anki.csv"

        fut = asyncio.get_running_loop().create_future()

        def on_result(res: ft.FilePickerResultEvent):
            if res.path:
                fut.set_result(res.path)
            else:
                fut.set_result("")

        sp = ft.FilePicker(on_result=on_result)
        app.page.overlay.append(sp)
        app.page.update()
        sp.save_file(allowed_extensions=["csv"], file_name=default_csv)
        path = await fut
        if not path:
            app.logger.info("Sauvegarde annulée par l'utilisateur.")
            return

        raw_source = app.generated_csv if app.generated_csv.strip() else csv_verified
        raw_path = path.replace(".csv", ".raw.csv")
        try:
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_source)
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_verified)
            app.logger.info("Exporté: %s", path)
            app.logger.info("Exporté (RAW): %s", raw_path)
        except Exception as e:
            app.logger.error("Échec d'écriture: %s", e)
            app.snack(f"Échec d'écriture: {e}", pal["err"])
            return

        if app.split_by_topic:
            try:
                _save_split_by_topic(csv_verified, path)
            except Exception as e:
                app.logger.error("Échec split par topic: %s", e)

    def _save_split_by_topic(csv_text: str, main_path: str):
        folder = os.path.dirname(main_path)
        rows = list(csv.reader(io.StringIO(csv_text)))
        if not rows:
            return
        header, data = rows[0], rows[1:]
        by_topic: dict[str, list[list[str]]] = {}
        for r in data:
            topic = (r[0] if len(r) > 0 else "Untitled").strip() or "Untitled"
            by_topic.setdefault(topic, []).append(r)
        for topic, items in by_topic.items():
            safe = re.sub(r"[^\w\- ]+", "_", topic)[:60].strip().replace(" ", "_") or "Untitled"
            out = os.path.join(folder, f"{safe}.anki.csv")
            with open(out, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow(header)
                w.writerows(items)
            app.logger.info("Deck par topic exporté: %s", out)

    # bind
    app._rows_to_csv_text = _rows_to_csv_text
    app._save_outputs = _save_outputs
    app._save_split_by_topic = _save_split_by_topic
