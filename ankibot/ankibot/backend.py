"""
Backend for Ankibot: Fact model, GenAI interface, prompts
"""

import csv
import io
import os
import re
import json
import time
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging
from fuzzywuzzy import fuzz

from ankibot.ui import app
from ankibot.utils import is_valid_json
from ankibot.config import DEFAULT_MODEL, load_config

# Google GenAI (optional)
try:
    from google import genai
    from google.genai import types
    from google.api_core.exceptions import InternalServerError
except Exception:  # library not installed or missing
    genai = None
    types = None
    InternalServerError = Exception


# ============================= Models ============================= #

@dataclass
class Fact:
    topic: str
    subtopic: Optional[str]
    fact: str
    source: Optional[str] = None


@dataclass
class GenAIConfig:
    model: str = DEFAULT_MODEL
    thinking_budget: int = -1  # 0=off, -1=auto
    temperature: float = 0.0


# ============================= Prompts ============================= #

from ankibot.prompts import (
    PROMPT_FACT_EXTRACTION,
    PROMPT_CSV_GENERATION_BASE,
    PROMPT_CSV_VERIFICATION,
)


# ============================= Backend ============================= #

class FlashcardBackend:
    def __init__(self, api_key: Optional[str], model: str = DEFAULT_MODEL, logger: Optional[logging.Logger] = None):
        self.cfg = load_config()
        self.api_key = (
            str(self.cfg.get("api_key")).strip()
        )
        self.client = genai.Client(api_key=self.api_key) if (genai and self.api_key) else None
        self.cfg = GenAIConfig(model=model, thinking_budget=-1, temperature=0.0)
        self.logger = logger or logging.getLogger("ankibot")  # Fallback to default logger

    async def _gen(self, prompt: str, type: str = "default") -> str:
        """Low-level GenAI call with retries."""
        if not self.client:
            raise RuntimeError("API key is missing. Set it in Settings or GEMINI_API_KEY.")

        config = types.GenerateContentConfig(
            temperature=self.cfg.temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=self.cfg.thinking_budget),
        )

        max_retries, delay = 7, 1.0
        last_err: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                def _call():
                    resp = self.client.models.generate_content(
                        model=self.cfg.model, contents=prompt, config=config
                    )
                    if not resp or resp.text is None or resp.text.strip() == "" or resp.text.strip() == "[]" or resp.text.strip().lower().startswith("i'm sorry") or resp.text.strip().lower().startswith("sorry,"):
                        raise InternalServerError(f"No response from model. Response was {resp.text if resp else 'None'}.")
                    # Check if the prompt is for fact extraction (match start of prompt)
                    if type == "fact_extraction":
                        #print(f"Raw fact extraction response:\n{resp.text}\n---")
                        if is_valid_json(resp.text.strip()):
                            return resp.text.strip()
                        cleaned = resp.text.strip()

                        # Strip code fences if present
                        if cleaned.startswith("```"):
                            cleaned = re.sub(r"^```[a-zA-Z0-9]*\n?", "", cleaned)
                            cleaned = re.sub(r"```$", "", cleaned).strip()

                        # If still not valid JSON, try to extract array only
                        if not is_valid_json(cleaned):
                            m = re.search(r"\[\s*{.*}\s*\]", cleaned, re.DOTALL)
                            if m:
                                cleaned = m.group(0)

                        # Try final JSON check
                        if not is_valid_json(cleaned):
                            self.logger.error(f"Invalid JSON output from model (facts). Raw text:\n{resp.text}\nCleaned:\n{cleaned}")
                            raise InternalServerError("Invalid JSON output for facts.")

                        return cleaned
                    
                    if type == "card_generation":
                        pass  # Future use
                    return (resp.text or "").strip()

                return await asyncio.to_thread(_call)
            except InternalServerError as e:
                last_err = e
                self.logger.error(f"GenAI error (InternalServerError) (attempt {attempt}) (sleeping for {delay} seconds): {e}")
                await asyncio.sleep(delay)
                delay *= 2
            except Exception as e:
                last_err = e
                self.logger.error(f"GenAI error (Exception) (attempt {attempt}) (sleeping for {delay} seconds): {e}")
                await asyncio.sleep(delay)
                delay *= 2
        raise RuntimeError(f"GenAI error: {last_err}. prompt was: {prompt}")

    async def extract_facts(self, chunk: str) -> List[Fact]:
        """Extract atomic facts from a text chunk."""
        text = await self._gen(PROMPT_FACT_EXTRACTION.format(chunk=chunk), type="fact_extraction")

        def try_parse_json(txt: str) -> Optional[List[Dict[str, Any]]]:
            try:
                return json.loads(txt)
            except Exception:
                return None

        # Step 1: Direct attempt
        data = try_parse_json(text)

        # Step 2: Extract JSON array with regex if extra text is around
        if not data:
            m = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
            if m:
                data = try_parse_json(m.group(0))

        # Step 3: Cleanup common LLM mistakes
        if not data:
            fixed = (
                text.replace("'", '"')              # single → double quotes
                    .replace("\n", " ")             # remove newlines inside
                    .replace(", ]", "]")            # trailing comma
                    .replace(",]", "]")
            )
            m = re.search(r"\[\s*{.*}\s*\]", fixed, re.DOTALL)
            if m:
                data = try_parse_json(m.group(0))

        if not data:
            self.logger.error(f"Fact extraction failed. Raw text was:\n{text}")
            return []

        # Validate keys and build Fact objects
        facts: List[Fact] = []
        for f in data:
            try:
                facts.append(
                    Fact(
                        topic=f.get("topic", "").strip(),
                        subtopic=f.get("subtopic"),
                        fact=f.get("fact", "").strip(),
                        source=f.get("source"),
                    )
                )
            except Exception as e:
                self.logger.error(f"Invalid fact entry skipped: {f}, error: {e}")
                continue

        return facts


    async def generate_csv(self, facts: List[Fact], reverse: bool, density_level: int, custom_add: str = "") -> str:
        """Generate an Anki-ready CSV string from extracted facts."""
        density_note = {
            1: "Low density: macro cards only, most important informations.",
            2: "Normal density: one card per atomic fact.",
            3: "High density: split steps, parameters, exceptions.",
        }.get(density_level, "Normal density: one card per atomic fact.")
        reverse_note = (
            "- For each card, ALSO create a reversed version if relevant."
            if reverse
            else "- Do not create reversed versions."
        )
        facts_json = json.dumps([f.__dict__ for f in facts], ensure_ascii=False)
        prompt = PROMPT_CSV_GENERATION_BASE.format(
            density_note=density_note, reverse_note=reverse_note, facts_json=facts_json, custom_add=custom_add or ""
        )
        return await self._gen(prompt)

    async def verify_csv(self, full_text: str, csv_text: str) -> str:
        """Verify CSV flashcards against source text and log detailed modifications."""
        # Parse original CSV
        original_cards = []
        try:
            csv_reader = csv.reader(io.StringIO(csv_text))
            headers = next(csv_reader, None)  # Skip header
            if headers:
                original_cards = [row for row in csv_reader]
        except Exception as e:
            self.logger.error(f"Error parsing original CSV: {e}")
            return csv_text  # Fallback to original if parsing fails

        # Generate verified CSV
        prompt = PROMPT_CSV_VERIFICATION.format(full_text=full_text, csv_text=csv_text)
        verified_csv = await self._gen(prompt)

        # Parse verified CSV
        verified_cards = []
        try:
            csv_reader = csv.reader(io.StringIO(verified_csv))
            headers = next(csv_reader, None)  # Skip header
            if headers:
                verified_cards = [row for row in csv_reader]
        except Exception as e:
            self.logger.error(f"Error parsing verified CSV: {e}")
            return csv_text  # Fallback to original if parsing fails

        # Create dicts for easier lookup (key: (Topic, Subtopic, Question) tuple, value: full row)
        def card_key(row):
            return (row[0], row[1], row[2]) if len(row) >= 3 else None

        # Normalize text for fuzzy matching (e.g., handle LaTeX, case, punctuation)
        def normalize_text(text):
            text = re.sub(r'\\\(.*?\\\)', 'MATH', text.lower().strip())  # Replace LaTeX with placeholder
            return re.sub(r'[.,?!]', '', text)  # Remove punctuation

        original_dict = {card_key(row): row for row in original_cards if card_key(row)}
        verified_dict = {card_key(row): row for row in verified_cards if card_key(row)}

        # Identify exact-match rewrites and unchanged (same key, but check if Answer/Source/Details differ)
        rewritten_cards = []
        unchanged_count = 0
        matched_keys = set()
        for key, verified_row in verified_dict.items():
            if key in original_dict:
                matched_keys.add(key)
                original_row = original_dict[key]
                if original_row[3:] != verified_row[3:]:  # Compare Answer, Source, Details
                    # Identify changed fields
                    changed_fields = []
                    if original_row[3] != verified_row[3]:
                        changed_fields.append("Answer")
                    if original_row[4] != verified_row[4]:
                        changed_fields.append("Source")
                    if original_row[5] != verified_row[5]:
                        changed_fields.append("Details")
                    rewritten_cards.append((original_row, verified_row, changed_fields, 100))  # Exact match, score=100
                else:
                    unchanged_count += 1

        # Remaining unpaired originals (potential removals) and verifieds (potential additions)
        unpaired_originals = [row for key, row in original_dict.items() if key not in matched_keys]
        unpaired_verifieds = [row for key, row in verified_dict.items() if key not in matched_keys]

        # Fuzzy matching for potential rewrites among unpaired
        similarity_threshold = 80  # fuzzywuzzy uses 0-100 scale
        fuzzy_rewritten = []
        removed_cards = []
        added_cards = []
        used_verified_indices = set()

        for orig_idx, original_row in enumerate(unpaired_originals):
            best_match = None
            best_score = 0
            best_changed_fields = []
            for ver_idx, verified_row in enumerate(unpaired_verifieds):
                if ver_idx in used_verified_indices:
                    continue
                # Compute fuzzy similarity: Combine token_sort_ratio and partial_ratio
                question_sort = fuzz.token_sort_ratio(
                    normalize_text(original_row[2]), normalize_text(verified_row[2])
                )
                question_partial = fuzz.partial_ratio(
                    normalize_text(original_row[2]), normalize_text(verified_row[2])
                )
                topic_sort = fuzz.token_sort_ratio(
                    normalize_text(original_row[0]), normalize_text(verified_row[0])
                )
                # Weighted average: 60% question token_sort, 20% question partial, 20% topic
                overall_sim = (0.6 * question_sort + 0.2 * question_partial + 0.2 * topic_sort)
                # Identify changed fields for potential match
                temp_changed_fields = []
                if original_row[0] != verified_row[0]:
                    temp_changed_fields.append("Topic")
                if original_row[1] != verified_row[1]:
                    temp_changed_fields.append("Subtopic")
                if original_row[2] != verified_row[2]:
                    temp_changed_fields.append("Question")
                if original_row[3] != verified_row[3]:
                    temp_changed_fields.append("Answer")
                if original_row[4] != verified_row[4]:
                    temp_changed_fields.append("Source")
                if original_row[5] != verified_row[5]:
                    temp_changed_fields.append("Details")
                if overall_sim > best_score:
                    best_score = overall_sim
                    best_match = (ver_idx, verified_row)
                    best_changed_fields = temp_changed_fields

            if best_score >= similarity_threshold:
                fuzzy_rewritten.append((original_row, best_match[1], best_changed_fields, best_score))
                used_verified_indices.add(best_match[0])
            else:
                removed_cards.append(original_row)

        # Remaining unpaired verifieds are true additions
        for ver_idx, verified_row in enumerate(unpaired_verifieds):
            if ver_idx not in used_verified_indices:
                added_cards.append(verified_row)

        # Logging modifications
        for card in removed_cards:
            self.logger.info(
                f"CSV Modification: Removed card (potential inaccurate, duplicate, or irrelevant) - "
                f"Topic: {card[0]}, Subtopic: {card[1]}, Question: {card[2]}, "
                f"Answer: {card[3]}, Source: {card[4]}, Details: {card[5]}"
            )

        for card in added_cards:
            self.logger.info(
                f"CSV Modification: Added new card - "
                f"Topic: {card[0]}, Subtopic: {card[1]}, Question: {card[2]}, "
                f"Answer: {card[3]}, Source: {card[4]}, Details: {card[5]}"
            )

        for original, verified, changed_fields, sim_score in rewritten_cards + fuzzy_rewritten:
            sim_note = f"exact match" if sim_score == 100 else f"fuzzy match, similarity={sim_score:.1f}"
            self.logger.info(
                f"CSV Modification: Rewrote card ({sim_note}, changed fields: {', '.join(changed_fields)}) - "
                f"Topic: {original[0]} → {verified[0]}, "
                f"Subtopic: {original[1]} → {verified[1]}, "
                f"Question: {original[2]} → {verified[2]}, "
                f"Answer: {original[3]} → {verified[3]}, "
                f"Source: {original[4]} → {verified[4]}, "
                f"Details: {original[5]} → {verified[5]}"
            )

        # High-level summary
        total_rewritten = len(rewritten_cards) + len(fuzzy_rewritten)
        self.logger.info(
            f"CSV Verification Summary: "
            f"{len(removed_cards)} cards removed, "
            f"{len(added_cards)} cards added, "
            f"{total_rewritten} cards rewritten (including {len(fuzzy_rewritten)} fuzzy matches), "
            f"{unchanged_count} cards unchanged."
        )

        return verified_csv