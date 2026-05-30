"""Tests for the Term data model."""

from __future__ import annotations

import pytest

from vn_financial_terms.models import ALLOWED_DOMAINS, Term


def test_term_basic():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    assert t.en == "Revenue"
    assert t.vi == "Doanh thu"
    assert t.domain == "accounting"


def test_term_optional_fields_default_none():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    assert t.en_abbr is None
    assert t.vi_abbr is None
    assert t.notes is None
    assert t.vas_ref is None
    assert t.ifrs_ref is None


def test_term_alt_vi_default_empty():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    assert t.alt_vi == ()
    assert t.alt_en == ()


def test_term_alt_vi_list_coerced_to_tuple():
    """YAML loader produces lists; __post_init__ must coerce to tuple."""
    t = Term(
        en="Fixed assets",
        vi="Tài sản cố định",
        domain="accounting",
        alt_vi=["Tài sản dài hạn hữu hình"],  # type: ignore[arg-type]
    )
    assert isinstance(t.alt_vi, tuple)
    assert "Tài sản dài hạn hữu hình" in t.alt_vi


def test_term_is_frozen():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    with pytest.raises(Exception):
        t.en = "something else"  # type: ignore[misc]


def test_term_invalid_en_raises():
    with pytest.raises(ValueError, match="Term.en"):
        Term(en="", vi="Doanh thu", domain="accounting")


def test_term_invalid_domain_raises():
    with pytest.raises(ValueError, match="Term.domain"):
        Term(en="Revenue", vi="Doanh thu", domain="invalid_domain")


def test_allowed_domains_complete():
    expected = {
        "accounting", "tax", "banking", "markets",
        "regulatory", "real_estate", "insurance", "macro",
    }
    assert ALLOWED_DOMAINS == expected


def test_term_to_dict_excludes_none():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    d = t.to_dict()
    assert "en" in d
    assert "vi" in d
    assert "domain" in d
    assert "en_abbr" not in d
    assert "notes" not in d


def test_term_to_dict_excludes_empty_tuple():
    t = Term(en="Revenue", vi="Doanh thu", domain="accounting")
    d = t.to_dict()
    assert "alt_vi" not in d
    assert "alt_en" not in d


def test_all_en_forms():
    t = Term(
        en="Fixed assets",
        vi="Tài sản cố định",
        en_abbr="FA",
        domain="accounting",
        alt_en=("Property, plant and equipment",),
    )
    forms = t.all_en_forms
    assert "Fixed assets" in forms
    assert "FA" in forms
    assert "Property, plant and equipment" in forms


def test_all_vi_forms():
    t = Term(
        en="Fixed assets",
        vi="Tài sản cố định",
        vi_abbr="TSCĐ",
        domain="accounting",
        alt_vi=("Tài sản dài hạn hữu hình",),
    )
    forms = t.all_vi_forms
    assert "Tài sản cố định" in forms
    assert "TSCĐ" in forms
    assert "Tài sản dài hạn hữu hình" in forms
