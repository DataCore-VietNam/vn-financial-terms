"""AI translation consistency — complete example.

Demonstrates how to use TerminologyGuide to generate a system prompt
and glossary block for LLM-assisted translation of Vietnamese financial
documents (books, reports, contracts) into English.

Usage
-----
    python examples/ai_translation.py

Or integrate the generated prompt directly into your LLM pipeline::

    import anthropic
    from vn_financial_terms import TerminologyGuide

    guide = TerminologyGuide(domains=["accounting", "tax"])
    system = guide.build_system_prompt(source="vi", target="en")

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": chapter_text}],
    )
"""

from vn_financial_terms import TerminologyGuide, build_translation_prompt

# ── 1. Full-book translation prompt ─────────────────────────────────────────
# Covers all 8 domains — use this for broad financial/legal books.
full_guide = TerminologyGuide()
print(f"Full guide: {len(full_guide)} terms across all domains")
print()

full_prompt = full_guide.build_system_prompt(source="vi", target="en")
print("=== System Prompt (first 800 chars) ===")
print(full_prompt[:800])
print("...\n")

# ── 2. Chapter-specific guide ────────────────────────────────────────────────
# Accounting + tax chapter: only load relevant domains.
chapter_guide = TerminologyGuide(domains=["accounting", "tax"])
chapter_prompt = chapter_guide.build_system_prompt(
    source="vi",
    target="en",
    include_notes=True,        # include translator notes
    include_abbreviations=True,
)
print(f"Chapter guide: {len(chapter_guide)} terms")

# ── 3. Export for external CAT tools ─────────────────────────────────────────
banking_guide = TerminologyGuide(domains=["banking"])

# SDL Trados / memoQ / OmegaT import format
csv_glossary = banking_guide.to_csv(source="vi", target="en")
print("\n=== CSV (first 400 chars) ===")
print(csv_glossary[:400])

# JSON for custom pipelines or vector databases
json_glossary = banking_guide.to_json(source="vi", target="en")
print("\n=== JSON (first 400 chars) ===")
print(json_glossary[:400])

# Markdown table for embedding in a prompt or Notion doc
md_glossary = banking_guide.to_markdown(source="vi", target="en")
print("\n=== Markdown (first 400 chars) ===")
print(md_glossary[:400])

# ── 4. Mid-conversation glossary block ───────────────────────────────────────
# When the API does not support system messages, inject into the user turn:
block = chapter_guide.build_glossary_block(source="vi", target="en", fmt="markdown")
user_message = f"""Please translate the following chapter. Use the glossary below.

{block}

---

Chương 3: Phân tích Báo cáo Tài chính

Doanh thu của công ty tăng 15% so với năm trước, đạt 2.500 tỷ đồng.
Lợi nhuận gộp đạt 800 tỷ đồng, tương đương biên lợi nhuận gộp 32%.
Tài sản cố định sau khấu hao còn 1.200 tỷ đồng (VAS 03).
"""
print("\n=== User message with injected glossary (first 600 chars) ===")
print(user_message[:600])

# ── 5. Convenience wrapper ───────────────────────────────────────────────────
quick_prompt = build_translation_prompt(
    source="vi", target="en", domains=["regulatory"]
)
print(f"\n=== Quick prompt for regulatory domain ({len(quick_prompt)} chars) ===")
print(quick_prompt[:300])
