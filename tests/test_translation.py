"""Tests for the AI-translation TerminologyGuide."""

from __future__ import annotations

from vn_financial_terms import TerminologyGuide, build_translation_prompt


def test_guide_all_domains():
    guide = TerminologyGuide()
    assert len(guide) > 100


def test_guide_single_domain():
    guide = TerminologyGuide(domains=["tax"])
    assert len(guide) > 0
    assert all(t.domain == "tax" for t in guide)


def test_guide_multi_domain():
    guide = TerminologyGuide(domains=["accounting", "tax"])
    domains = {t.domain for t in guide}
    assert domains == {"accounting", "tax"}


def test_guide_filter():
    full = TerminologyGuide()
    tax = full.filter(["tax"])
    assert len(tax) > 0
    assert all(t.domain == "tax" for t in tax)


def test_guide_len():
    guide = TerminologyGuide(domains=["accounting"])
    assert len(guide) > 0


def test_guide_repr():
    guide = TerminologyGuide(domains=["accounting"])
    r = repr(guide)
    assert "TerminologyGuide" in r
    assert "accounting" in r


def test_build_system_prompt_vi_to_en():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="vi", target="en")
    assert "Vietnamese-to-English" in prompt
    assert "Mandatory Glossary" in prompt
    assert "Doanh thu" in prompt  # vi source term present
    assert "Revenue" in prompt  # en target term present


def test_build_system_prompt_en_to_vi():
    guide = TerminologyGuide(domains=["accounting"])
    prompt = guide.build_system_prompt(source="en", target="vi")
    assert "English-to-Vietnamese" in prompt


def test_build_system_prompt_abbreviations():
    guide = TerminologyGuide(domains=["tax"])
    prompt = guide.build_system_prompt(source="vi", target="en", include_abbreviations=True)
    assert "Abbreviations" in prompt
    # TNDN should appear somewhere
    assert "TNDN" in prompt


def test_build_glossary_block_markdown():
    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="markdown")
    assert "| Vietnamese |" in block


def test_build_glossary_block_json():
    import json

    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="json")
    data = json.loads(block)
    assert isinstance(data, list)


def test_build_glossary_block_csv():
    guide = TerminologyGuide(domains=["accounting"])
    block = guide.build_glossary_block(fmt="csv")
    assert "vi,en,domain" in block


def test_to_json():
    import json

    guide = TerminologyGuide(domains=["tax"])
    out = guide.to_json()
    data = json.loads(out)
    assert isinstance(data, list)
    assert all("vi" in row and "en" in row for row in data)


def test_to_csv():
    guide = TerminologyGuide(domains=["tax"])
    out = guide.to_csv()
    assert "TNDN" in out or "Thuế thu nhập" in out


def test_to_markdown():
    guide = TerminologyGuide(domains=["tax"])
    out = guide.to_markdown()
    assert "|" in out
    assert "Vietnamese" in out


def test_build_translation_prompt_convenience():
    prompt = build_translation_prompt(source="vi", target="en", domains=["accounting"])
    assert "Mandatory Glossary" in prompt
    assert "Revenue" in prompt


def test_guide_terms_explicit():
    from vn_financial_terms import lookup

    t = lookup("Revenue")
    assert t is not None
    guide = TerminologyGuide(terms=[t])
    assert len(guide) == 1
    assert next(iter(guide)).en == "Revenue"
