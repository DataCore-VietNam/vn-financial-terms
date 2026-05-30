"""Data model for a single glossary entry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_DOMAINS: frozenset[str] = frozenset(
    {
        "accounting",
        "banking",
        "insurance",
        "macro",
        "markets",
        "real_estate",
        "regulatory",
        "tax",
    }
)


@dataclass(frozen=True)
class Term:
    """A single bilingual glossary entry.

    Attributes
    ----------
    en:
        Canonical English term (e.g. ``"Revenue"``).
    vi:
        Canonical Vietnamese term (e.g. ``"Doanh thu"``).
    domain:
        One of ``accounting``, ``tax``, ``banking``, ``markets``,
        ``regulatory``, ``real_estate``, ``insurance``, ``macro``.
    en_abbr:
        Optional English abbreviation (e.g. ``"EBITDA"``).
    vi_abbr:
        Optional Vietnamese abbreviation (e.g. ``"TNDN"``).
    alt_vi:
        Additional Vietnamese surface forms (synonyms, alternate
        spellings). All are indexed for case-insensitive lookup.
    alt_en:
        Additional English surface forms.
    vas_ref:
        Optional Vietnamese Accounting Standard reference (e.g. ``"VAS 14"``).
    ifrs_ref:
        Optional IFRS / IAS reference (e.g. ``"IFRS 15"``).
    definition_en:
        Optional plain-English definition.
    definition_vi:
        Optional Vietnamese definition.
    notes:
        Translation guidance — preferred phrasing, register caveats,
        disambiguation hints. Surfaced by :class:`TerminologyGuide`
        when building AI translation prompts.
    """

    en: str
    vi: str
    domain: str
    en_abbr: str | None = None
    vi_abbr: str | None = None
    alt_vi: tuple[str, ...] = field(default_factory=tuple)
    alt_en: tuple[str, ...] = field(default_factory=tuple)
    vas_ref: str | None = None
    ifrs_ref: str | None = None
    definition_en: str | None = None
    definition_vi: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.en or not isinstance(self.en, str):
            raise ValueError("Term.en must be a non-empty string")
        if not self.vi or not isinstance(self.vi, str):
            raise ValueError("Term.vi must be a non-empty string")
        if self.domain not in ALLOWED_DOMAINS:
            raise ValueError(
                f"Term.domain must be one of {sorted(ALLOWED_DOMAINS)!r}, "
                f"got {self.domain!r}"
            )
        # Coerce lists → tuples (YAML loader produces lists).
        if isinstance(self.alt_vi, list):
            object.__setattr__(self, "alt_vi", tuple(self.alt_vi))
        if isinstance(self.alt_en, list):
            object.__setattr__(self, "alt_en", tuple(self.alt_en))

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict with ``None`` / empty-tuple fields removed."""
        result: dict[str, Any] = {}
        for k, v in asdict(self).items():
            if v is None:
                continue
            if isinstance(v, (list, tuple)) and len(v) == 0:
                continue
            result[k] = v
        return result

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def all_vi_forms(self) -> tuple[str, ...]:
        """All Vietnamese surface forms: canonical + abbreviation + alternates."""
        forms: list[str] = [self.vi]
        if self.vi_abbr:
            forms.append(self.vi_abbr)
        forms.extend(self.alt_vi)
        return tuple(forms)

    @property
    def all_en_forms(self) -> tuple[str, ...]:
        """All English surface forms: canonical + abbreviation + alternates."""
        forms: list[str] = [self.en]
        if self.en_abbr:
            forms.append(self.en_abbr)
        forms.extend(self.alt_en)
        return tuple(forms)
