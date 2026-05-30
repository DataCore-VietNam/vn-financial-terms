"""Glossary loading and lookup primitives.

YAML files in :mod:`vn_financial_terms.data` are loaded once at import time
into an in-memory list of :class:`~vn_financial_terms.models.Term` objects
and indexed by every surface form (en, vi, en_abbr, vi_abbr, alt_vi,
alt_en) for case-insensitive lookup.
"""

from __future__ import annotations

import csv
import io
import json
from importlib import resources
from typing import Any, Literal

import yaml

from vn_financial_terms.models import Term

ExportFormat = Literal["csv", "json", "markdown"]


def _load_all() -> list[Term]:
    """Load every YAML file shipped under ``vn_financial_terms.data``."""
    terms: list[Term] = []
    data_pkg = resources.files("vn_financial_terms.data")
    for entry in sorted(data_pkg.iterdir(), key=lambda p: p.name):
        if not entry.name.endswith((".yaml", ".yml")):
            continue
        with entry.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or []
        if not isinstance(raw, list):
            raise ValueError(f"Expected a YAML list in {entry.name}, got {type(raw).__name__}")
        for i, row in enumerate(raw):
            if not isinstance(row, dict):
                raise ValueError(f"Entry #{i} in {entry.name} is not a mapping")
            cleaned: dict[str, Any] = {}
            for k, v in row.items():
                if k in ("alt_vi", "alt_en"):
                    cleaned[k] = tuple(v) if isinstance(v, list) else ()
                elif isinstance(v, str):
                    cleaned[k] = v.strip()
                else:
                    cleaned[k] = v
            terms.append(Term(**cleaned))
    return terms


def _build_index(terms: list[Term]) -> dict[str, Term]:
    """Build a case-insensitive surface-form -> Term lookup table.

    On collisions the first-loaded term wins (deterministic across
    identical YAML files).
    """
    index: dict[str, Term] = {}
    for term in terms:
        for surface in (*term.all_en_forms, *term.all_vi_forms):
            if not surface:
                continue
            key = surface.casefold().strip()
            index.setdefault(key, term)
    return index


_TERMS: list[Term] = _load_all()
_INDEX: dict[str, Term] = _build_index(_TERMS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def lookup(term: str) -> Term | None:
    """Look up a term by any surface form (case-insensitive).

    Searches English, Vietnamese, abbreviations, and alternate forms.
    Returns ``None`` when no entry matches.

    Examples
    --------
    >>> lookup("EBITDA").vi_abbr
    'EBITDA'
    >>> lookup("doanh thu").en
    'Revenue'
    >>> lookup("  TSCĐ  ").en
    'Fixed assets'
    """
    if not term:
        return None
    return _INDEX.get(term.casefold().strip())


def translate(term: str, to: Literal["en", "vi"]) -> str | None:
    """Translate *term* to the requested language.

    Parameters
    ----------
    term:
        Any surface form of the term (case-insensitive).
    to:
        Target language — ``"en"`` for English, ``"vi"`` for Vietnamese.

    Returns
    -------
    The translated canonical form, or ``None`` if *term* is unknown.

    Raises
    ------
    ValueError
        If *to* is not ``"en"`` or ``"vi"``.
    """
    if to not in ("en", "vi"):
        raise ValueError(f"`to` must be 'en' or 'vi', got {to!r}")
    entry = lookup(term)
    if entry is None:
        return None
    return entry.en if to == "en" else entry.vi


def search(
    query: str,
    *,
    domains: list[str] | None = None,
) -> list[Term]:
    """Partial-match search across all surface forms and definitions.

    Parameters
    ----------
    query:
        Substring to search for (case-insensitive).
    domains:
        Optional domain filter (e.g. ``["accounting", "tax"]``).

    Returns
    -------
    All matching terms, in load order (alphabetical by domain then file).

    Examples
    --------
    >>> results = search("thuế")
    >>> any(t.domain == "tax" for t in results)
    True
    """
    needle = query.casefold().strip()
    if not needle:
        return []

    pool = _TERMS
    if domains:
        domain_set = {d.casefold() for d in domains}
        pool = [t for t in _TERMS if t.domain.casefold() in domain_set]

    results: list[Term] = []
    for term in pool:
        surfaces: list[str] = list(term.all_en_forms) + list(term.all_vi_forms)
        if term.definition_en:
            surfaces.append(term.definition_en)
        if term.definition_vi:
            surfaces.append(term.definition_vi)
        if term.notes:
            surfaces.append(term.notes)
        if any(needle in s.casefold() for s in surfaces if s):
            results.append(term)
    return results


def all_terms() -> list[Term]:
    """Return a copy of every loaded term."""
    return list(_TERMS)


def by_domain(domain: str) -> list[Term]:
    """Return all terms whose ``domain`` matches (case-insensitive)."""
    needle = domain.casefold().strip()
    return [t for t in _TERMS if t.domain.casefold() == needle]


def export(
    fmt: ExportFormat = "csv",
    *,
    source: Literal["vi", "en"] = "vi",
    target: Literal["en", "vi"] = "en",
    domains: list[str] | None = None,
) -> str:
    """Export the full glossary (or a domain subset) as CSV, JSON, or Markdown.

    Parameters
    ----------
    fmt:
        Output format: ``"csv"``, ``"json"``, or ``"markdown"``.
    source:
        Source-language column (``"vi"`` or ``"en"``).
    target:
        Target-language column.
    domains:
        Optional domain filter.

    Returns
    -------
    A UTF-8 string in the requested format.

    Examples
    --------
    >>> print(export("csv", source="vi", target="en", domains=["tax"]))
    vi,en,domain,...
    """
    pool = by_domain(domains[0]) if domains and len(domains) == 1 else all_terms()
    if domains and len(domains) > 1:
        domain_set = {d.casefold() for d in domains}
        pool = [t for t in _TERMS if t.domain.casefold() in domain_set]

    if fmt == "json":
        rows = []
        for t in pool:
            row: dict[str, object] = {
                source: t.vi if source == "vi" else t.en,
                target: t.en if target == "en" else t.vi,
                "domain": t.domain,
            }
            if t.en_abbr:
                row["en_abbr"] = t.en_abbr
            if t.vi_abbr:
                row["vi_abbr"] = t.vi_abbr
            if t.notes:
                row["notes"] = t.notes
            rows.append(row)
        return json.dumps(rows, ensure_ascii=False, indent=2)

    if fmt == "markdown":
        src_label = "Vietnamese" if source == "vi" else "English"
        tgt_label = "English" if target == "en" else "Vietnamese"
        lines = [
            f"| {src_label} | {tgt_label} | Domain | Notes |",
            "| --- | --- | --- | --- |",
        ]
        for t in sorted(pool, key=lambda x: (x.domain, x.en)):
            src_val = t.vi if source == "vi" else t.en
            tgt_val = t.en if target == "en" else t.vi
            lines.append(f"| {src_val} | {tgt_val} | {t.domain} | {t.notes or ''} |")
        return "\n".join(lines)

    # Default: CSV
    buf = io.StringIO()
    src_col = "vi" if source == "vi" else "en"
    tgt_col = "en" if target == "en" else "vi"
    writer = csv.DictWriter(
        buf,
        fieldnames=[src_col, tgt_col, "domain", "en_abbr", "vi_abbr", "notes"],
        extrasaction="ignore",
    )
    writer.writeheader()
    for t in pool:
        writer.writerow(
            {
                src_col: t.vi if source == "vi" else t.en,
                tgt_col: t.en if target == "en" else t.vi,
                "domain": t.domain,
                "en_abbr": t.en_abbr or "",
                "vi_abbr": t.vi_abbr or "",
                "notes": t.notes or "",
            }
        )
    return buf.getvalue()
