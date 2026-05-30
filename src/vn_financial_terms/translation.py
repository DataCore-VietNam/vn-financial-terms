"""AI-translation consistency toolkit.

Drop a :class:`TerminologyGuide` into any LLM translation workflow to pin
every glossary term to its canonical translation, eliminating drift across
chapters or documents.

Quick start
-----------
Build a system prompt for a Vietnamese -> English book translation::

    from vn_financial_terms import TerminologyGuide

    guide = TerminologyGuide(domains=["accounting", "tax", "banking"])
    system_prompt = guide.build_system_prompt(source="vi", target="en")
    # Pass system_prompt to your LLM's system role.

Export the glossary to feed external CAT tools or memory files::

    guide.to_csv()        # SDL Trados, memoQ, OmegaT
    guide.to_json()       # custom pipelines
    guide.to_markdown()   # embed in prompts or docs

Filter to just the domains relevant to a chapter::

    chapter_guide = guide.filter(["real_estate", "regulatory"])
    block = chapter_guide.build_glossary_block()
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Literal

from vn_financial_terms.glossary import all_terms, by_domain

if TYPE_CHECKING:
    from vn_financial_terms.models import Term

Lang = Literal["vi", "en"]


class TerminologyGuide:
    """Compile and export a consistent bilingual glossary for AI translation.

    Parameters
    ----------
    domains:
        Restrict to one or more domains (e.g. ``["accounting", "tax"]``).
        Pass ``None`` (default) to include all domains.
    terms:
        Explicit list of :class:`~vn_financial_terms.models.Term` objects.
        When provided, *domains* is ignored.

    Examples
    --------
    >>> guide = TerminologyGuide(domains=["accounting"])
    >>> len(guide) > 0
    True
    >>> "Mandatory Glossary" in guide.build_system_prompt()
    True
    """

    def __init__(
        self,
        domains: list[str] | None = None,
        terms: list[Term] | None = None,
    ) -> None:
        if terms is not None:
            self._terms: list[Term] = list(terms)
        elif domains:
            seen: set[tuple[str, str]] = set()
            self._terms = []
            for d in domains:
                for t in by_domain(d):
                    key = (t.en, t.vi)
                    if key not in seen:
                        seen.add(key)
                        self._terms.append(t)
        else:
            self._terms = all_terms()

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def build_system_prompt(
        self,
        source: Lang = "vi",
        target: Lang = "en",
        *,
        include_notes: bool = True,
        include_abbreviations: bool = True,
    ) -> str:
        """Return a ready-to-use system prompt for AI-assisted translation.

        Embed the returned string as the ``system`` role when calling any
        LLM to translate a financial document.  The prompt instructs the
        model to follow the mandatory glossary and explains abbreviation
        and register conventions.

        Parameters
        ----------
        source:
            Source language (``"vi"`` or ``"en"``).
        target:
            Target language (``"vi"`` or ``"en"``).
        include_notes:
            Append per-term translation notes where available.
        include_abbreviations:
            Include a separate abbreviation-mapping table.

        Returns
        -------
        str
            A complete system prompt string.
        """
        lang_names: dict[str, str] = {"vi": "Vietnamese", "en": "English"}
        src_name = lang_names[source]
        tgt_name = lang_names[target]

        lines: list[str] = [
            f"You are an expert {src_name}-to-{tgt_name} financial and legal translator.",
            "Your primary objective is accuracy combined with strict terminological",
            "consistency — the same source term must always produce the same target",
            "term throughout the entire document.",
            "",
            "## Mandatory Glossary",
            "",
            "The following terms MUST be translated exactly as shown.",
            "Never paraphrase, substitute, or vary these translations:",
            "",
            self._glossary_table(source, target, include_notes=include_notes),
        ]

        if include_abbreviations:
            abbr_block = self._abbreviation_table(source, target)
            if abbr_block:
                lines += [
                    "",
                    "## Abbreviations",
                    "",
                    "Preserve these abbreviations unchanged unless context requires expansion:",
                    "",
                    abbr_block,
                ]

        lines += [
            "",
            "## Translation Rules",
            "",
            "1. Apply every term in the glossary exactly as written (case, spacing,",
            "   hyphenation).",
            "2. When a source abbreviation appears (e.g. TNDN, TSCĐ), use the",
            "   corresponding target abbreviation if one exists; otherwise use the",
            "   full target form.",
            "3. For source terms with no direct target equivalent, keep the source",
            f"   term and add a {tgt_name} gloss in parentheses on first occurrence,",
            "   e.g.: *Thông tư* (Circular).",
            "4. Do NOT translate proper nouns: institution names (Ngân hàng Nhà nước,",
            "   HOSE, HNX, Bộ Tài chính), legal instrument numbers, and standard",
            "   codes (VAS 14, IFRS 15, Basel III) must remain unchanged.",
            "5. Preserve all numerical values, units, percentages, and date formats.",
            "6. Maintain source formatting: headings, tables, bullet lists, footnotes.",
            "7. When a term has a VAS reference and an IFRS reference that differ in",
            "   meaning, follow the VAS framing unless the document is explicitly",
            "   IFRS-based.",
        ]

        return "\n".join(lines)

    def build_glossary_block(
        self,
        source: Lang = "vi",
        target: Lang = "en",
        *,
        fmt: Literal["markdown", "json", "csv"] = "markdown",
    ) -> str:
        """Return a compact glossary block to inject into a *user* message.

        Use this when your API does not support system messages, or when
        you want to pass the glossary mid-conversation.

        Parameters
        ----------
        source:
            Source language.
        target:
            Target language.
        fmt:
            Output format: ``"markdown"`` (default), ``"json"``, or ``"csv"``.
        """
        if fmt == "json":
            return self.to_json(source=source, target=target)
        if fmt == "csv":
            return self.to_csv(source=source, target=target)
        return self._glossary_table(source, target, include_notes=True)

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def to_json(
        self,
        source: Lang = "vi",
        target: Lang = "en",
        *,
        indent: int = 2,
    ) -> str:
        """Serialise the glossary to a JSON string (UTF-8)."""
        rows: list[dict[str, object]] = []
        for t in self._terms:
            row: dict[str, object] = {
                source: t.vi if source == "vi" else t.en,
                target: t.en if target == "en" else t.vi,
                "domain": t.domain,
            }
            if t.en_abbr:
                row["en_abbr"] = t.en_abbr
            if t.vi_abbr:
                row["vi_abbr"] = t.vi_abbr
            if t.vas_ref:
                row["vas_ref"] = t.vas_ref
            if t.ifrs_ref:
                row["ifrs_ref"] = t.ifrs_ref
            if t.notes:
                row["notes"] = t.notes
            rows.append(row)
        return json.dumps(rows, ensure_ascii=False, indent=indent)

    def to_csv(
        self,
        source: Lang = "vi",
        target: Lang = "en",
    ) -> str:
        """Serialise the glossary to a CSV string (UTF-8).

        Compatible with SDL Trados, memoQ, OmegaT, and similar CAT tools.
        """
        buf = io.StringIO()
        src_col = "vi" if source == "vi" else "en"
        tgt_col = "en" if target == "en" else "vi"
        writer = csv.DictWriter(
            buf,
            fieldnames=[
                src_col,
                tgt_col,
                "domain",
                "en_abbr",
                "vi_abbr",
                "vas_ref",
                "ifrs_ref",
                "notes",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        for t in self._terms:
            writer.writerow(
                {
                    src_col: t.vi if source == "vi" else t.en,
                    tgt_col: t.en if target == "en" else t.vi,
                    "domain": t.domain,
                    "en_abbr": t.en_abbr or "",
                    "vi_abbr": t.vi_abbr or "",
                    "vas_ref": t.vas_ref or "",
                    "ifrs_ref": t.ifrs_ref or "",
                    "notes": t.notes or "",
                }
            )
        return buf.getvalue()

    def to_markdown(
        self,
        source: Lang = "vi",
        target: Lang = "en",
    ) -> str:
        """Return a Markdown table of the full glossary."""
        return self._glossary_table(source, target, include_notes=True)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter(self, domains: list[str]) -> TerminologyGuide:
        """Return a new guide restricted to the specified domains.

        Examples
        --------
        >>> full = TerminologyGuide()
        >>> tax_guide = full.filter(["tax"])
        >>> all(t.domain == "tax" for t in tax_guide._terms)
        True
        """
        needle = {d.casefold() for d in domains}
        return TerminologyGuide(terms=[t for t in self._terms if t.domain.casefold() in needle])

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._terms)

    def __iter__(self) -> Iterator[Term]:
        return iter(self._terms)

    def __repr__(self) -> str:
        domains = sorted({t.domain for t in self._terms})
        return f"TerminologyGuide(terms={len(self._terms)}, domains={domains!r})"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _glossary_table(
        self,
        source: Lang,
        target: Lang,
        *,
        include_notes: bool = False,
    ) -> str:
        src_label = "Vietnamese" if source == "vi" else "English"
        tgt_label = "English" if target == "en" else "Vietnamese"
        cols = [src_label, tgt_label, "Domain"]
        if include_notes:
            cols.append("Notes")

        sep = "| " + " | ".join("---" for _ in cols) + " |"
        header = "| " + " | ".join(cols) + " |"
        rows = [header, sep]

        for t in sorted(self._terms, key=lambda x: (x.domain, x.en.casefold())):
            src_val = t.vi if source == "vi" else t.en
            tgt_val = t.en if target == "en" else t.vi
            cells = [src_val, tgt_val, t.domain]
            if include_notes:
                cells.append(t.notes or "")
            rows.append("| " + " | ".join(cells) + " |")

        return "\n".join(rows)

    def _abbreviation_table(self, source: Lang, target: Lang) -> str:
        pairs: list[tuple[str, str]] = []
        seen: set[str] = set()
        for t in self._terms:
            src_abbr = t.vi_abbr if source == "vi" else t.en_abbr
            tgt_abbr = t.en_abbr if target == "en" else t.vi_abbr
            if src_abbr and src_abbr not in seen:
                seen.add(src_abbr)
                pairs.append((src_abbr, tgt_abbr or src_abbr))

        if not pairs:
            return ""

        lines = ["| Source | Target |", "| --- | --- |"]
        for src, tgt in sorted(pairs):
            lines.append(f"| {src} | {tgt} |")
        return "\n".join(lines)


def build_translation_prompt(
    source: Lang = "vi",
    target: Lang = "en",
    domains: list[str] | None = None,
) -> str:
    """Convenience wrapper: build a system prompt from the full glossary.

    Parameters
    ----------
    source:
        Source language.
    target:
        Target language.
    domains:
        Optional domain filter. ``None`` includes all domains.

    Returns
    -------
    str
        A complete system prompt ready to pass to an LLM.

    Examples
    --------
    >>> prompt = build_translation_prompt(source="vi", target="en",
    ...                                   domains=["accounting"])
    >>> "Mandatory Glossary" in prompt
    True
    """
    guide = TerminologyGuide(domains=domains)
    return guide.build_system_prompt(source=source, target=target)
