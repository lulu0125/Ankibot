"""
Utility functions for Ankibot
"""

import os
import csv
import re
import json
import pdfplumber
import tiktoken
from typing import Any, Dict, List


def with_opacity(opacity: float, hex_color: str) -> str:
    """Add alpha to a hex color string."""
    if not hex_color or not hex_color.startswith("#") or len(hex_color) != 7:
        return hex_color
    a = hex(int(max(0, min(1, opacity)) * 255))[2:].upper().zfill(2)
    return f"#{a}{hex_color[1:]}"


def extract_text_from_pdf(path: str) -> str:
    """Extract plain text from PDF file."""
    try:
        with pdfplumber.open(path) as pdf:
            return "\n\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception:
        return ""


def chunk_text(text: str, max_tokens: int = 2000, overlap: int = 120,
               encoding_name: str = "cl100k_base") -> List[str]:
    """Split text into overlapping chunks (token-aware)."""
    enc = tiktoken.get_encoding(encoding_name)
    overlap = max(0, min(overlap, max_tokens // 2))

    def tok(s: str) -> List[int]:
        return enc.encode(s)

    def detok(toks: List[int]) -> str:
        return enc.decode(toks)

    def last_n(tokens: List[int], n: int) -> List[int]:
        return tokens[-n:] if n > 0 and len(tokens) > n else tokens[:]

    def split_long_tokens(tokens: List[int], win: int, ovlp: int) -> List[List[int]]:
        if not tokens:
            return []
        parts, stride, i = [], max(1, win - ovlp), 0
        while i < len(tokens):
            parts.append(tokens[i: i + win])
            if i + win >= len(tokens):
                break
            i += stride
        return parts

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sep_toks = tok("\n\n")
    chunks: List[str] = []
    buf: List[int] = []

    for p in paragraphs:
        p_toks = tok(p)
        if len(p_toks) > max_tokens:
            if buf:
                chunks.append(detok(buf).strip())
                buf = []
            for window in split_long_tokens(p_toks, max_tokens, overlap):
                chunks.append(detok(window).strip())
            continue
        add_len = len(p_toks) + len(sep_toks)
        if buf and len(buf) + add_len > max_tokens:
            chunks.append(detok(buf).strip())
            buf = last_n(buf, overlap)
        buf.extend(p_toks)
        buf.extend(sep_toks)
    if buf:
        chunks.append(detok(buf).strip())
    return chunks


def deduplicate_facts(facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate facts by their text content."""
    seen, uniq = set(), []
    for f in facts:
        key = (f.get("fact", "").strip().lower())
        if key and key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


def is_valid_json(text: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(text)
        return True
    except Exception:
        return False
