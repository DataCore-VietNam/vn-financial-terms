"""Tests for TerminologyGuide and build_translation_prompt."""

from __future__ import annotations

import json

from vn_financial_terms import TerminologyGuide, build_translation_prompt, lookup

# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_guide_all_domains_has_all_terms():
    guide = TerminologyGuide()
    assert len(guide) > 150


def test_guide_single_domain():
    guide = TerminologyGuide(domains=["tax"])
    assert len(guide) > 0
    assert all(t.domain == "tax" for t in guide)


def test_guide_multi_domain():
    guide = TerminologyGuide(domains=["accounting", "tax"])
    domains = {t.domain for t in guide}
    assert domains == {"accounting", "tax"}


def test_guide_explicit_terms():
    t = lookup("Revenue")
    assert t is not None
    guide = TerminologyGuide(terms=[t])
    assert len(guide) == 1
    assert next(iter(guide)).en == "Revenue"


def test_guide_explicit_terms_ignores_domains():
    t = lookup("Revenue")
    guide = TerminologyGuide(domains=["banking"], terms=[t])
    assert len(guide) == 1


def test_guide_no_duplicate_terms():
    guide = TerminologyGuide(domains=["accounting", "accounting"])
    single = TerminologyGuide(domains=["accounting"])
    assert len(guide) == len(single)


# ---------------------------------------------------------------------------
# filter
# ---------------------------------------------------------------------------


def test_filter_single_domain():
    full = TerminologyGuide()
    tax = full.filter(["tax"])
    assert len(tax) > 0
    assert all(t.domain == "tax" for t in tax)


def test_filter_multi_domain():
    full = TerminologyGuide()
    subset = full.filter(["banking", "macro"])
    domains = {t.domain for t in subset}
    assert domains == {"banking", "macro"}


def test_filter_unknown_domain_returns_empty():
    full = TerminologyGuide()
    empty = full.filter(["not_a_domain"])
    assert len(empty) == 0


def test_filter_returns_new_guide():
    full = TerminologyGuide()
    sub = full.filter(["tax"])
    assert len(sub) < len(full)


# ---------------------------------------------------------------------------
# __len__, __iter__, __repr__
# ---------------------------------------------------------------------------


def test_len():
    guide = TerminologyGuide(domains=["accounting"])
    assert len(guide) > 0


def test_iter():
    guide = TerminologyGuide(domains=["tax"])
    terms = list(guide)
    assert len(terms) > 0


def test_repr():
    guide = TerminologyGuide(domains=["accounting"])
    r = repr(guide)
    assert "TerminologyGuide" in r
    assert "accounting" in r


# ---------------------------------------------------------------------------
# build_system_prompt
# ---------------------------------------------------------------------------


def test_system_prompt_vi_to_en_contains_mandatory_glossary():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="vi", target="en")
    assert "Mandatory Glossary" in prompt


def test_system_prompt_contains_source_and_target_terms():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="vi", target="en")
    assert "Doanh thu" in prompt  # VI source
    assert "Revenue" in prompt  # EN target


def test_system_prompt_vi_to_en_language_names():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="vi", target="en")
    assert "Vietnamese-to-English" in prompt


def test_system_prompt_en_to_vi_language_names():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="en", target="vi")
    assert "English-to-Vietnamese" in prompt


def test_system_prompt_contains_abbreviation_table():
    guide = TerminologyGuide(domains=["tax"])
    prompt = guide.build_system_prompt(source="vi", target="en", include_abbreviations=True)
    assert "Abbreviations" in prompt
    assert "TNDN" in prompt


def test_system_prompt_no_abbreviations():
    guide = TerminologyGuide(domains=["tax"])
    prompt = guide.build_system_prompt(source="vi", target="en", include_abbreviations=False)
    assert "Abbreviations" not in prompt


def test_system_prompt_contains_translation_rules():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt()
    assert "Translation Rules" in prompt


def test_system_prompt_all_domains():
    guide = TerminologyGuide()
    prompt = guide.build_system_prompt(source="vi", target="en")
    # All canonical EN terms from accounting should appear
    assert "Revenue" in prompt
    assert "Non-performing loan" in prompt


# ---------------------------------------------------------------------------
# build_glossary_block
# ---------------------------------------------------------------------------


def test_glossary_block_markdown():
    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="markdown")
    assert "| Vietnamese |" in block
    assert "Doanh thu" in block


def test_glossary_block_json():
    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="json")
    data = json.loads(block)
    assert isinstance(data, list)


def test_glossary_block_csv():
    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="csv")
    assert "vi,en,domain" in block


# ---------------------------------------------------------------------------
# to_json / to_csv / to_markdown
# ---------------------------------------------------------------------------


def test_to_json_valid():
    guide = TerminologyGuide(domains=["tax"])
    data = json.loads(guide.to_json())
    assert isinstance(data, list)
    assert all("vi" in row and "en" in row for row in data)


def test_to_json_includes_abbr_when_present():
    guide = TerminologyGuide(domains=["tax"])
    data = json.loads(guide.to_json())
    tndn_row = next((r for r in data if r.get("vi_abbr") == "TNDN"), None)
    assert tndn_row is not None


def test_to_json_en_to_vi():
    guide = TerminologyGuide(domains=["tax"])
    data = json.loads(guide.to_json(source="en", target="vi"))
    assert all("en" in row and "vi" in row for row in data)


def test_to_csv_header():
    guide = TerminologyGuide(domains=["banking"])
    csv = guide.to_csv()
    assert csv.startswith("vi,en,domain")


def test_to_csv_contains_known_term():
    guide = TerminologyGuide(domains=["banking"])
    csv = guide.to_csv()
    assert "Nợ xấu" in csv
    assert "Non-performing loan" in csv


def test_to_markdown_has_table():
    guide = TerminologyGuide(domains=["markets"])
    md = guide.to_markdown()
    assert "| Vietnamese |" in md
    assert "| --- |" in md


def test_to_markdown_sorted_by_domain_then_en():
    guide = TerminologyGuide(domains=["accounting", "tax"])
    md = guide.to_markdown()
    rows = [
        row
        for row in md.splitlines()
        if row.startswith("|") and "---" not in row and "Vietnamese" not in row
    ]
    # accounting comes before tax alphabetically
    domains_seen = [row.split("|")[3].strip() for row in rows]
    accounting_idx = next(i for i, d in enumerate(domains_seen) if d == "accounting")
    tax_idx = next(i for i, d in enumerate(domains_seen) if d == "tax")
    assert accounting_idx < tax_idx


# ---------------------------------------------------------------------------
# build_translation_prompt convenience function
# ---------------------------------------------------------------------------


def test_build_translation_prompt_vi_to_en():
    prompt = build_translation_prompt(source="vi", target="en", domains=["accounting"])
    assert "Mandatory Glossary" in prompt
    assert "Revenue" in prompt


def test_build_translation_prompt_all_domains():
    prompt = build_translation_prompt()
    assert "Mandatory Glossary" in prompt
    assert len(prompt) > 5000  # comprehensive prompt


def test_build_translation_prompt_domain_filter():
    tax_prompt = build_translation_prompt(domains=["tax"])
    # Tax-specific term should appear
    assert "Thuế" in tax_prompt or "thuế" in tax_prompt.lower()
