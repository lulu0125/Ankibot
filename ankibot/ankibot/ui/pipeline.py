from __future__ import annotations

import os
import io
import csv
import asyncio
import traceback
import flet as ft

from ankibot.ui import app
from ankibot.utils import extract_text_from_pdf, chunk_text, deduplicate_facts
from ankibot.backend import Fact


def attach(app):
    async def _start_pipeline(pasted_text: str):
        app.cancel_event = asyncio.Event()
        if app.progress:
            app.progress.value = 0.0
        if app.progress_label:
            app.progress_label.value = ""
        app.page.update()
        try:
            await _pipeline(pasted_text, app.new_pipeline)
        except asyncio.CancelledError:
            app.logger.warning("Pipeline annulé.")
            app.snack("Opération annulée", app._palette()["warn"])
        except Exception as e:
            app.logger.error("Erreur fatale: %s\n%s", e, traceback.format_exc())
            app.snack(f"Erreur: {e}", app._palette()["err"])
        finally:
            if app.progress:
                app.progress.value = None  # stop animation
            app.page.update()

    def _set_stage(label: str, value: float):
        if app.progress:
            app.progress.value = value
        if app.progress_label:
            app.progress_label.value = label
        app.page.update()

    async def _pipeline(pasted_text: str, newpipeline: bool):
        pal = app._palette()
        if not app.selected_files and not pasted_text.strip():
            app.snack("Sélectionne un fichier ou colle du texte", pal["err"])
            return
        if not getattr(app.backend, "client", None):
            app.snack("Clé API manquante (Paramètres)", pal["err"])
            return

        if newpipeline:
                # Stage 1: Read & concat
                _set_stage("Lecture des entrées…", 0.02)
                texts: list[str] = []
                for idx, path in enumerate(app.selected_files):
                    if app.cancel_event.is_set():
                        raise asyncio.CancelledError
                    if path.lower().endswith(".pdf"):
                        t = await asyncio.to_thread(extract_text_from_pdf, path)
                    else:
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                t = f.read()
                        except Exception as e:
                            app.logger.error("Erreur lecture '%s': %s", path, e)
                            t = ""
                    if not t.strip():
                        app.logger.warning("Aucun texte détecté dans: %s", os.path.basename(path))
                    texts.append(t)
                    if app.progress:
                        app.progress.value = 0.02 + 0.10 * ((idx + 1) / max(1, len(app.selected_files)))
                        app.page.update()
                if pasted_text.strip():
                    texts.append(pasted_text)
                app.source_full_text = "\n\n".join(t for t in texts if t)
                if not app.source_full_text.strip():
                    app.snack("Aucun texte exploitable.", pal["err"])
                    return

                # Stage 2: Chunk
                _set_stage("Découpage en segments…", 0.16)
                chunks = await asyncio.to_thread(chunk_text, app.source_full_text, 2000, 120)
                app.logger.info("Segments: %d", len(chunks))
                _set_stage(f"Découpage terminé → {len(chunks)} segments", 0.20)

                # Stage 3: Extract facts (parallel with adaptive throttling)
                _set_stage("Extraction des faits…", 0.22)
                max_workers = min(8, (os.cpu_count() or 4))
                semaphore = asyncio.Semaphore(max_workers)
                facts_all: list[tuple[int, Fact]] = []  # (chunk_id, fact)

                async def extract_one(i: int, ch: str):
                    async with semaphore:
                        if app.cancel_event.is_set():
                            return []
                        app.logger.info("Segment %d/%d…", i + 1, len(chunks))
                        try:
                            facts = await app.backend.extract_facts(ch)
                            app.logger.info("Segment %d: %d faits", i + 1, len(facts))
                            return [(i, f) for f in facts]
                        except Exception as e:
                            app.logger.error("Erreur extraction (segment %d): %s", i + 1, e)
                            return []

                tasks = [extract_one(i, ch) for i, ch in enumerate(chunks)]
                done = 0
                for coro in asyncio.as_completed(tasks):
                    if app.cancel_event.is_set():
                        raise asyncio.CancelledError
                    res = await coro
                    facts_all.extend(res)
                    done += 1
                    _set_stage(f"Extraction des faits… ({done}/{len(chunks)})", 0.22 + 0.28 * (done / max(1, len(chunks))))

                # Stage 4: Deduplicate globally, keeping the first chunk_id for duplicates
                _set_stage("Déduplication…", 0.52)
                facts_unique: list[tuple[int, Fact]] = []
                seen = set()
                for chunk_id, f in facts_all:
                    key = tuple(sorted(f.__dict__.items()))  # Assuming facts are deduped based on exact field matches
                    if key not in seen:
                        seen.add(key)
                        facts_unique.append((chunk_id, f))
                app.all_facts = [f for _, f in facts_unique]
                app.logger.info("✅ %d faits uniques", len(app.all_facts))
                _set_stage(f"Faits uniques: {len(app.all_facts)}", 0.57)
                app._refresh_fact_preview()

                # Group facts by chunk_id
                from collections import defaultdict
                facts_by_chunk: defaultdict[int, list[Fact]] = defaultdict(list)
                for chunk_id, f in facts_unique:
                    facts_by_chunk[chunk_id].append(f)

                # Stage 5: Generate CSV per chunk (parallel)
                _set_stage("Génération des cartes…", 0.61)
                active_chunks = sorted(facts_by_chunk.keys())
                semaphore = asyncio.Semaphore(max_workers)  # Reuse semaphore

                async def generate_one(chunk_id: int):
                    async with semaphore:
                        if app.cancel_event.is_set():
                            return chunk_id, ""
                        facts = facts_by_chunk[chunk_id]
                        try:
                            csv_str = await app.backend.generate_csv(
                                facts, reverse=app.reverse_card, density_level=app.density_level, custom_add=app.custom_add
                            )
                            return chunk_id, csv_str
                        except Exception as e:
                            app.logger.error("Erreur génération CSV (segment %d): %s", chunk_id + 1, e)
                            return chunk_id, ""

                tasks = [generate_one(chunk_id) for chunk_id in active_chunks]
                generated_dict = {}
                done = 0
                for coro in asyncio.as_completed(tasks):
                    if app.cancel_event.is_set():
                        raise asyncio.CancelledError
                    chunk_id, csv_str = await coro
                    if csv_str:
                        generated_dict[chunk_id] = csv_str
                    done += 1
                    _set_stage(f"Génération des cartes… ({done}/{len(active_chunks)})", 0.61 + 0.09 * (done / max(1, len(active_chunks))))

                # Combine generated CSVs into one
                if generated_dict:
                    # Assume all CSVs have the same header; take from first
                    first_csv = next(iter(generated_dict.values()))
                    header = first_csv.splitlines()[0]
                    data_lines = []
                    for csv_str in generated_dict.values():
                        lines = csv_str.splitlines()[1:]
                        data_lines.extend(l for l in lines if l.strip())
                    app.generated_csv = header + '\n' + '\n'.join(data_lines)
                else:
                    app.generated_csv = ""
                _set_stage("Cartes générées (brut)", 0.70)

                # Fill editable table from generated CSV
                app._parse_cards_to_rows(app.generated_csv)
                app._refresh_cards_preview()

                if app.cancel_event.is_set():
                    raise asyncio.CancelledError

                # Prepare current_csv_per_chunk for verification
                current_csv_per_chunk = generated_dict.copy()

                # Stage 6: Verify CSV per chunk (configurable runs)
                app.verification_runs = 2 if app.double_check else 1
                for run in range(app.verification_runs or 1):  # Default to 1 run
                    _set_stage(f"Vérification & correction ({run+1}/{app.verification_runs or 1})…", 0.75 + 0.08 * run)

                    async def verify_one(chunk_id: int):
                        async with semaphore:
                            if app.cancel_event.is_set():
                                return chunk_id, current_csv_per_chunk[chunk_id]
                            chunk_text = chunks[chunk_id]
                            csv_to_verify = current_csv_per_chunk[chunk_id]
                            try:
                                verified_csv = await app.backend.verify_csv(chunk_text, csv_to_verify)
                                return chunk_id, verified_csv
                            except Exception as e:
                                app.logger.warning(f"Erreur vérification CSV (segment {chunk_id+1}, run {run+1}): %s — utilisation du CSV précédent.", e)
                                return chunk_id, csv_to_verify

                    tasks = [verify_one(chunk_id) for chunk_id in active_chunks]
                    done = 0
                    verified_dict = {}
                    for coro in asyncio.as_completed(tasks):
                        if app.cancel_event.is_set():
                            raise asyncio.CancelledError
                        chunk_id, verified_csv = await coro
                        verified_dict[chunk_id] = verified_csv
                        done += 1
                        # Approximate sub-progress within the run
                        sub_prog = (done / max(1, len(active_chunks))) * 0.08
                        _set_stage(f"Vérification & correction ({run+1}/{app.verification_runs or 1})… ({done}/{len(active_chunks)})", 0.75 + 0.08 * run + sub_prog)

                    current_csv_per_chunk = verified_dict

                    # Combine verified CSVs for preview
                    if verified_dict:
                        first_csv = next(iter(verified_dict.values()))
                        header = first_csv.splitlines()[0]
                        data_lines = []
                        for csv_str in verified_dict.values():
                            lines = csv_str.splitlines()[1:]
                            data_lines.extend(l for l in lines if l.strip())
                        app.verified_csv = header + '\n' + '\n'.join(data_lines)
                    else:
                        app.verified_csv = ""

                    app._parse_cards_to_rows(app.verified_csv)
                    app._refresh_cards_preview()

                _set_stage("Vérification terminée", 0.95)

                # Stage 7: Save (picker + options)
                _set_stage("Terminé ✅ — Cliquez sur Exporter pour sauvegarder", 1.0)
                app.snack("Cartes prêtes ! Cliquez sur Exporter pour sauvegarder.", pal["ok"])

                # Stats
                app._update_deck_stats()
                app.snack("Deck(s) généré(s)", pal["ok"])
        else:
            # Stage 1: Read & concat
            _set_stage("Lecture des entrées…", 0.02)
            texts: list[str] = []
            for idx, path in enumerate(app.selected_files):
                if app.cancel_event.is_set():
                    raise asyncio.CancelledError
                if path.lower().endswith(".pdf"):
                    t = await asyncio.to_thread(extract_text_from_pdf, path)
                else:
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            t = f.read()
                    except Exception as e:
                        app.logger.error("Erreur lecture '%s': %s", path, e)
                        t = ""
                if not t.strip():
                    app.logger.warning("Aucun texte détecté dans: %s", os.path.basename(path))
                texts.append(t)
                if app.progress:
                    app.progress.value = 0.02 + 0.10 * ((idx + 1) / max(1, len(app.selected_files)))
                    app.page.update()
            if pasted_text.strip():
                texts.append(pasted_text)
            app.source_full_text = "\n\n".join(t for t in texts if t)
            if not app.source_full_text.strip():
                app.snack("Aucun texte exploitable.", pal["err"])
                return

            # Stage 2: Chunk
            _set_stage("Découpage en segments…", 0.16)
            chunks = await asyncio.to_thread(chunk_text, app.source_full_text, 2000, 120)
            app.logger.info("Segments: %d", len(chunks))
            _set_stage(f"Découpage terminé → {len(chunks)} segments", 0.20)

            # Stage 3: Extract facts (parallel with adaptive throttling)
            _set_stage("Extraction des faits…", 0.22)
            max_workers = min(8, (os.cpu_count() or 4))
            semaphore = asyncio.Semaphore(max_workers)
            facts_all: list[Fact] = []

            async def extract_one(i: int, ch: str):
                async with semaphore:
                    if app.cancel_event.is_set():
                        return []
                    app.logger.info("Segment %d/%d…", i + 1, len(chunks))
                    try:
                        facts = await app.backend.extract_facts(ch)
                        app.logger.info("Segment %d: %d faits", i + 1, len(facts))
                        return facts
                    except Exception as e:
                        app.logger.error("Erreur extraction (segment %d): %s", i + 1, e)
                        return []

            tasks = [extract_one(i, ch) for i, ch in enumerate(chunks)]
            done = 0
            for coro in asyncio.as_completed(tasks):
                if app.cancel_event.is_set():
                    raise asyncio.CancelledError
                res = await coro
                facts_all.extend(res)
                done += 1
                _set_stage(f"Extraction des faits… ({done}/{len(chunks)})", 0.22 + 0.28 * (done / max(1, len(chunks))))


            # Stage 4: Deduplicate
            _set_stage("Déduplication…", 0.52)

            # Convert Fact objects → dict → dedup → back to Fact objects
            facts_all = await asyncio.to_thread(
                lambda: [Fact(**f) for f in deduplicate_facts([f.__dict__ for f in facts_all])]
            )

            app.all_facts = facts_all
            app.logger.info("✅ %d faits uniques", len(app.all_facts))
            _set_stage(f"Faits uniques: {len(app.all_facts)}", 0.57)
            app._refresh_fact_preview()


            # Stage 5: Generate CSV
            _set_stage("Génération des cartes…", 0.61)
            try:
                app.generated_csv = await app.backend.generate_csv(
                    app.all_facts, reverse=app.reverse_card, density_level=app.density_level, custom_add=app.custom_add
                )
            except Exception as e:
                app.logger.error("Erreur génération CSV: %s", e)
                app.snack(f"Erreur génération CSV: {e}", pal["err"])
                return
            _set_stage("Cartes générées (brut)", 0.70)

            # Fill editable table from generated CSV
            app._parse_cards_to_rows(app.generated_csv)
            app._refresh_cards_preview()

            if app.cancel_event.is_set():
                raise asyncio.CancelledError

            # Stage 6: Verify CSV (configurable runs)
            app.verification_runs = 2 if app.double_check else 1
            for i in range(app.verification_runs or 1):  # Default to 1 run
                _set_stage(f"Vérification & correction ({i+1}/{app.verification_runs or 1})…", 0.75 + 0.08 * i)
                file2 = app.generated_csv
                try:
                    app.verified_csv = await app.backend.verify_csv(app.source_full_text, file2)
                    app._parse_cards_to_rows(app.verified_csv)
                    app._refresh_cards_preview()
                    file2 = app.verified_csv
                except Exception as e:
                    app.logger.warning(f"Erreur vérification CSV ({i+1}/{app.verification_runs or 1}): %s — utilisation du CSV précédent.", e)
                    break  # Stop on error, keep the last valid CSV
            _set_stage("Vérification terminée", 0.95)

            # Stage 7: Save (picker + options)
            _set_stage("Terminé ✅ — Cliquez sur Exporter pour sauvegarder", 1.0)
            app.snack("Cartes prêtes ! Cliquez sur Exporter pour sauvegarder.", pal["ok"])

            # Stats
            app._update_deck_stats()
            app.snack("Deck(s) généré(s)", pal["ok"])

    # bind
    app._start_pipeline = _start_pipeline
    app._pipeline = _pipeline
    app._set_stage = _set_stage
