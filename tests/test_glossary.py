"""Tests for the public glossary API."""

from __future__ import annotations

import pytest

from vn_financial_terms import Term, all_terms, by_domain, export, lookup, search, translate

# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------


def test_lookup_by_english_term():
    term = lookup("Revenue")
    assert term is not None
    assert term.vi == "Doanh thu"
    assert term.domain == "accounting"


def test_lookup_by_vietnamese_term():
    term = lookup("Doanh thu")
    assert term is not None
    assert term.en == "Revenue"


def test_lookup_is_case_insensitive():
    a = lookup("revenue")
    b = lookup("REVENUE")
    c = lookup("ReVeNuE")
    assert a is not None
    assert a is b is c


def test_lookup_strips_whitespace():
    assert lookup("  Revenue  ") == lookup("Revenue")


def test_lookup_by_english_abbreviation():
    term = lookup("EBITDA")
    assert term is not None
    assert "Lợi nhuận" in term.vi


def test_lookup_by_vietnamese_abbreviation():
    term = lookup("TNDN")
    assert term is not None
    assert term.en == "Corporate income tax"
    assert term.domain == "tax"


def test_lookup_unknown_returns_none():
    assert lookup("nonexistent term xyz") is None
    assert lookup("") is None


def test_lookup_fixed_assets_with_diacritics():
    term = lookup("TSCĐ")
    assert term is not None
    assert term.en == "Fixed assets"
    assert term.vas_ref == "VAS 03"


def test_lookup_fixed_assets_alt_vi():
    """alt_vi forms must be indexed."""
    by_main = lookup("Tài sản cố định")
    by_alt = lookup("Tài sản dài hạn hữu hình")
    assert by_main is not None
    assert by_alt is not None
    assert by_main is by_alt


def test_lookup_hose():
    hose = lookup("HOSE")
    assert hose is not None
    assert hose.domain == "markets"
    assert "Hồ Chí Minh" in hose.vi


def test_lookup_npl():
    npl = lookup("NPL")
    assert npl is not None
    assert npl.vi == "Nợ xấu"


def test_lookup_vcsh():
    term = lookup("VCSH")
    assert term is not None
    assert term.en == "Owner's equity"


# ---------------------------------------------------------------------------
# translate
# ---------------------------------------------------------------------------


def test_translate_to_english():
    assert translate("Doanh thu", to="en") == "Revenue"
    assert translate("TSCĐ", to="en") == "Fixed assets"


def test_translate_to_vietnamese():
    assert translate("Revenue", to="vi") == "Doanh thu"
    assert translate("EBITDA", to="vi").startswith("Lợi nhuận trước lãi vay")


def test_translate_unknown_returns_none():
    assert translate("nope", to="en") is None
    assert translate("nope", to="vi") is None


def test_translate_invalid_target_raises():
    with pytest.raises(ValueError):
        translate("Revenue", to="fr")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# all_terms / by_domain
# ---------------------------------------------------------------------------


def test_all_terms_returns_terms():
    terms = all_terms()
    assert len(terms) > 100, f"expected 100+ terms, got {len(terms)}"
    assert all(isinstance(t, Term) for t in terms)


def test_all_terms_returns_copy():
    before = len(all_terms())
    snap = all_terms()
    snap.clear()
    assert len(all_terms()) == before


def test_by_domain_accounting():
    terms = by_domain("accounting")
    assert len(terms) >= 30
    assert all(t.domain == "accounting" for t in terms)


def test_by_domain_tax():
    terms = by_domain("tax")
    assert len(terms) >= 15
    assert all(t.domain == "tax" for t in terms)


def test_by_domain_banking():
    terms = by_domain("banking")
    assert len(terms) >= 15


def test_by_domain_is_case_insensitive():
    assert by_domain("BANKING") == by_domain("banking")


def test_by_domain_unknown_returns_empty():
    assert by_domain("not_a_domain") == []


def test_domain_coverage():
    seen = {t.domain for t in all_terms()}
    for domain in (
        "accounting",
        "tax",
        "banking",
        "markets",
        "regulatory",
        "real_estate",
        "insurance",
        "macro",
    ):
        assert domain in seen, f"missing entries for domain {domain!r}"


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_partial_match():
    results = search("thuế")
    assert len(results) > 0
    assert any(t.domain == "tax" for t in results)


def test_search_english_substring():
    results = search("income")
    assert any("income" in t.en.lower() for t in results)


def test_search_case_insensitive():
    lower = search("revenue")
    upper = search("REVENUE")
    assert set(id(t) for t in lower) == set(id(t) for t in upper)


def test_search_with_domain_filter():
    results = search("lợi nhuận", domains=["accounting"])
    assert all(t.domain == "accounting" for t in results)


def test_search_empty_returns_empty():
    assert search("") == []


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


def test_export_csv():
    csv_out = export("csv", source="vi", target="en")
    assert "vi,en,domain" in csv_out
    assert "Doanh thu" in csv_out


def test_export_json():
    import json

    json_out = export("json", source="vi", target="en")
    data = json.loads(json_out)
    assert isinstance(data, list)
    assert all("vi" in row and "en" in row for row in data)


def test_export_markdown():
    md = export("markdown", source="vi", target="en")
    assert "| Vietnamese |" in md
    assert "| --- |" in md


def test_export_with_domain_filter():
    csv_out = export("csv", source="vi", target="en", domains=["tax"])
    rows = csv_out.strip().splitlines()
    # header + at least one data row
    assert len(rows) >= 2
