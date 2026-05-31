"""Tests for the public glossary API."""

from __future__ import annotations

import json

import pytest

from vn_financial_terms import (
    Term,
    all_terms,
    by_domain,
    export,
    lookup,
    search,
    translate,
)
from vn_financial_terms.models import ALLOWED_DOMAINS

# ---------------------------------------------------------------------------
# lookup — basic
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
    a, b, c = lookup("revenue"), lookup("REVENUE"), lookup("ReVeNuE")
    assert a is not None and a is b is c


def test_lookup_strips_whitespace():
    assert lookup("  Revenue  ") is lookup("Revenue")


def test_lookup_empty_returns_none():
    assert lookup("") is None


def test_lookup_unknown_returns_none():
    assert lookup("xyzzy_not_a_term_12345") is None


# ---------------------------------------------------------------------------
# lookup — abbreviations
# ---------------------------------------------------------------------------


def test_lookup_by_en_abbreviation():
    t = lookup("EBITDA")
    assert t is not None
    assert "Lợi nhuận" in t.vi


def test_lookup_by_vi_abbreviation_tndn():
    t = lookup("TNDN")
    assert t is not None
    assert t.en == "Corporate income tax"
    assert t.domain == "tax"


def test_lookup_by_vi_abbreviation_with_diacritics():
    t = lookup("TSCĐ")
    assert t is not None
    assert t.en == "Fixed assets"


def test_lookup_vcsh():
    t = lookup("VCSH")
    assert t is not None
    assert t.en == "Owner's equity"


def test_lookup_npl():
    t = lookup("NPL")
    assert t is not None
    assert t.vi == "Nợ xấu"
    assert t.domain == "banking"


def test_lookup_hose():
    t = lookup("HOSE")
    assert t is not None
    assert t.domain == "markets"
    assert "Hồ Chí Minh" in t.vi


def test_lookup_hnx():
    t = lookup("HNX")
    assert t is not None
    assert t.domain == "markets"


def test_lookup_gdp():
    t = lookup("GDP")
    assert t is not None
    assert t.domain == "macro"


def test_lookup_cit():
    t = lookup("CIT")
    assert t is not None
    assert t.domain == "tax"


def test_lookup_car():
    t = lookup("CAR")
    assert t is not None
    assert t.domain == "banking"


# ---------------------------------------------------------------------------
# lookup — alt_vi / alt_en alternate forms
# ---------------------------------------------------------------------------


def test_lookup_alt_vi_resolves_to_same_term():
    by_main = lookup("Tài sản cố định")
    by_alt = lookup("Tài sản dài hạn hữu hình")
    assert by_main is not None
    assert by_alt is not None
    assert by_main is by_alt


def test_lookup_alt_vi_current_assets():
    by_main = lookup("Tài sản ngắn hạn")
    by_old = lookup("Tài sản lưu động")
    assert by_main is not None
    assert by_old is not None
    assert by_main is by_old


# ---------------------------------------------------------------------------
# translate
# ---------------------------------------------------------------------------


def test_translate_vi_to_en():
    assert translate("Doanh thu", to="en") == "Revenue"
    assert translate("TSCĐ", to="en") == "Fixed assets"
    assert translate("Nợ xấu", to="en") == "Non-performing loan"


def test_translate_en_to_vi():
    assert translate("Revenue", to="vi") == "Doanh thu"
    assert translate("EBITDA", to="vi").startswith("Lợi nhuận trước lãi vay")


def test_translate_abbreviation_to_en():
    assert translate("TNDN", to="en") == "Corporate income tax"
    assert translate("GTGT", to="en") == "Value added tax"


def test_translate_unknown_returns_none():
    assert translate("no_such_term_xyz", to="en") is None
    assert translate("no_such_term_xyz", to="vi") is None


def test_translate_invalid_lang_raises():
    with pytest.raises(ValueError):
        translate("Revenue", to="fr")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# all_terms
# ---------------------------------------------------------------------------


def test_all_terms_count():
    terms = all_terms()
    assert len(terms) > 150, f"expected 150+ terms, got {len(terms)}"


def test_all_terms_all_are_term_instances():
    assert all(isinstance(t, Term) for t in all_terms())


def test_all_terms_returns_copy():
    snap = all_terms()
    before = len(snap)
    snap.clear()
    assert len(all_terms()) == before


def test_all_terms_domains_covered():
    seen = {t.domain for t in all_terms()}
    assert seen == ALLOWED_DOMAINS


# ---------------------------------------------------------------------------
# by_domain
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "domain,min_count",
    [
        ("accounting", 30),
        ("tax", 15),
        ("banking", 15),
        ("markets", 15),
        ("regulatory", 10),
        ("real_estate", 10),
        ("insurance", 8),
        ("macro", 10),
    ],
)
def test_by_domain_minimum_counts(domain, min_count):
    terms = by_domain(domain)
    assert len(terms) >= min_count, f"{domain}: expected >={min_count}, got {len(terms)}"
    assert all(t.domain == domain for t in terms)


def test_by_domain_case_insensitive():
    assert by_domain("BANKING") == by_domain("banking")
    assert by_domain("Accounting") == by_domain("accounting")


def test_by_domain_unknown_empty():
    assert by_domain("not_a_real_domain") == []


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_vietnamese_substring():
    results = search("thuế")
    assert len(results) > 0
    assert any(t.domain == "tax" for t in results)


def test_search_english_substring():
    results = search("income")
    assert any("income" in t.en.lower() for t in results)


def test_search_case_insensitive():
    lower = {id(t) for t in search("revenue")}
    upper = {id(t) for t in search("REVENUE")}
    assert lower == upper


def test_search_with_domain_filter():
    results = search("lợi nhuận", domains=["accounting"])
    assert len(results) > 0
    assert all(t.domain == "accounting" for t in results)


def test_search_multi_domain_filter():
    results = search("risk", domains=["banking", "insurance"])
    assert all(t.domain in ("banking", "insurance") for t in results)


def test_search_empty_query_returns_empty():
    assert search("") == []


def test_search_no_match_returns_empty():
    assert search("xyzzy_no_match_12345") == []


def test_search_hits_notes_field():
    # "VAS" appears in notes of many accounting terms
    results = search("VAS", domains=["accounting"])
    assert len(results) > 0


def test_search_hits_definition_field():
    results = search("proxy for operating cash")
    assert len(results) > 0
    assert results[0].en_abbr == "EBITDA"


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


def test_export_csv_structure():
    out = export("csv", source="vi", target="en")
    lines = out.strip().splitlines()
    assert lines[0] == "vi,en,domain,en_abbr,vi_abbr,notes"
    assert len(lines) > 100  # header + 100+ data rows


def test_export_csv_contains_known_term():
    out = export("csv", source="vi", target="en")
    assert "Doanh thu" in out
    assert "Revenue" in out


def test_export_json_valid():
    out = export("json", source="vi", target="en")
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) > 100
    assert all("vi" in row and "en" in row and "domain" in row for row in data)


def test_export_json_domain_filter():
    out = export("json", source="vi", target="en", domains=["tax"])
    data = json.loads(out)
    assert len(data) > 0
    assert all(row["domain"] == "tax" for row in data)


def test_export_markdown_structure():
    md = export("markdown", source="vi", target="en")
    assert "| Vietnamese |" in md
    assert "| English |" in md
    assert "| --- |" in md


def test_export_markdown_domain_filter():
    md = export("markdown", source="vi", target="en", domains=["banking"])
    assert "banking" in md


def test_export_en_to_vi():
    out = export("csv", source="en", target="vi")
    lines = out.strip().splitlines()
    assert lines[0].startswith("en,vi")


def test_export_multi_domain_filter():
    out = export("json", source="vi", target="en", domains=["tax", "accounting"])
    data = json.loads(out)
    domains = {row["domain"] for row in data}
    assert domains == {"tax", "accounting"}
