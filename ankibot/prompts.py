"""
ankibot.prompts
----------------
Centralized prompt templates for Ankibot's GenAI backend.
Each prompt is designed for explicit formatting via `.format()`.
"""

# ================================================================= #
#                            FACT EXTRACTION                        #
# ================================================================= #

PROMPT_FACT_EXTRACTION = r"""
You are a top-tier educational content analyst and flashcard creator.

Extract **every atomic fact** from the provided French text, with no hallucinations or omissions.

Output must be a **valid JSON array**. Each element is an object with EXACTLY these keys:
- "topic": string
- "subtopic": string or null
- "fact": string (single atomic fact, in French, no multiple facts in one item)
- "source": string or null (page number, heading, or other reference if available)

Output format requirements:
- Double quotes only (no single quotes).
- No trailing commas.
- Do not include explanations or comments outside JSON.
- Output only the JSON array, nothing else.
- Escape all backslashes properly

Guidelines:
- Include definitions, rules, processes, cause-effect, exceptions, formulas, numbers, key data.
- Each fact must be atomic and self-contained (one idea per item).
- Avoid duplicates.
- Latex/Mathjax should be handled properly. If some are detected, the structure must strictly be written as \\( ... \\). Remove all $ symbols and ensure each formula has exactly one opening \\( and one closing \\).
- Strictly base facts only on the provided text.
- Keep facts in French.

Text to analyze:
{chunk}
"""

# ================================================================= #
#                        CSV GENERATION BASE                        #
# ================================================================= #

PROMPT_CSV_GENERATION_BASE = r'''
You are an expert Anki flashcard creator.

Given the following JSON array of facts, generate an **Anki-ready CSV** with EXACTLY this header:

"Topic","Subtopic","Question","Answer","Source","Details"

Requirements:
- Output must be valid CSV with one header line and one line per card.
- Each field enclosed in double quotes.
- If a field contains a double quote ("), escape it by doubling the quote (e.g., He said "hello" becomes "He said ""hello""").
- Each card corresponds to ONE atomic fact, expressed as a clear Q&A.
- Questions must be concise, answerable within 10 seconds, and in French.
- Answers must be concise, correct, and in French.
- "Source": copy from the fact or "None" if unknown.
- "Details": optional helpful context, kept short (max 20 words).
- Do not repeat cards, no near-duplicates.
- Latex/Mathjax should be handled properly. If some are detected, the structure must strictly be written as \( ... \). Ensure each formula has exactly one opening \( and one closing \).
- Output **CSV text only**, no explanations or formatting.
- Do not add extra columns or change the header.

Granularity level: {density_note}
Reversed cards: {reverse_note}

Custom addition rules:
{custom_add}

Facts JSON:
{facts_json}
'''

# ================================================================= #
#                           CSV VERIFICATION                        #
# ================================================================= #

PROMPT_CSV_VERIFICATION = r"""
You are a fact-checker and CSV validator.

Task: verify and correct the flashcards in the CSV below against the original French source text.

Instructions:
- Keep EXACTLY the same header: "Topic","Subtopic","Question","Answer","Source","Details"
- If a card is inaccurate, unclear, or hallucinated: rewrite it correctly.
- If a card is vague, duplicated, malformed, or irrelevant: remove it.
- Do not remove cards unless they are clearly wrong, duplicated, or meaningless. When in doubt, keep the card but correct it.
- Keep only valid, clear, atomic flashcards.
- Latex/Mathjax should be handled properly. If some are detected, the structure must strictly be written as \( ... \). Ensure each formula has exactly one opening \( and one closing \). \\(...\\) is not allowed.
- Do not invent new information not in the source.
- Output only corrected CSV text, with header and valid rows.
- Do not include explanations, commentary, or formatting outside the CSV.
- Ensure correct CSV formatting.

Original source text:
{full_text}

CSV to verify:
{csv_text}
"""