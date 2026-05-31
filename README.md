# vn-financial-terms

[![CI](https://github.com/DataCore-VietNam/vn-financial-terms/actions/workflows/ci.yml/badge.svg)](https://github.com/DataCore-VietNam/vn-financial-terms/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vn-financial-terms)](https://pypi.org/project/vn-financial-terms/)
[![Python](https://img.shields.io/pypi/pyversions/vn-financial-terms)](https://pypi.org/project/vn-financial-terms/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/DataCore-VietNam/vn-financial-terms/actions)

Bilingual **(Vietnamese ↔ English)** glossary of financial, accounting, tax, banking, and regulatory terminology used in Vietnam — with IFRS/VAS cross-references, abbreviations, alternate forms, and translation guidance notes.

Built for two use cases:

- **Programmatic lookup** — resolve any surface form (term, abbreviation, alternate spelling) to a canonical `Term` object
- **AI translation** — generate a system prompt that forces LLMs to use consistent terminology when translating financial books, reports, or contracts

---

## Contents

- [Coverage](#coverage)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Full API reference](#full-api-reference)
- [AI translation workflow](#ai-translation-workflow)
- [Data format](#data-format)
- [Adding terms](#adding-terms)
- [Development](#development)
- [License](#license)

---

## Coverage

230+ terms across 8 domains:

| Domain | Terms | Examples |
| --- | --- | --- |
| `accounting` | 55 | Revenue / Doanh thu, EBITDA, Fixed assets / Tài sản cố định |
| `banking` | 42 | NPL / Nợ xấu, CAR, NIM, AML/PCRT, SBV/NHNN |
| `tax` | 31 | CIT/TNDN, VAT/GTGT, PIT/TNCN, Transfer pricing / Chuyển giá |
| `markets` | 35 | HOSE, HNX, VN-Index, IPO, FOL / Room ngoại |
| `regulatory` | 25 | SSC/UBCKNN, VAS, VSA, Thông tư, Nghị định |
| `real_estate` | 20 | QSDĐ, Sổ đỏ, KCN, FAR / Hệ số sử dụng đất |
| `insurance` | 18 | Phí bảo hiểm, Tái bảo hiểm, Loss ratio |
| `macro` | 23 | GDP, CPI, FDI, Tỷ giá trung tâm, Nợ công |

Each entry can carry: canonical EN/VI forms, EN/VI abbreviations, alternate surface forms (`alt_vi`, `alt_en`), VAS reference, IFRS/IAS reference, plain-language definitions, and translator notes.

---

## Installation

```bash
pip install vn-financial-terms
```

Requires Python 3.10+. The only runtime dependency is `pyyaml`.

---

## Quick start

```python
from vn_financial_terms import lookup, translate, search, by_domain, export

# ── Lookup by any surface form ──────────────────────────────────────────────
term = lookup("EBITDA")
print(term.en)       # Earnings before interest, taxes, depreciation, and amortization
print(term.vi)       # Lợi nhuận trước lãi vay, thuế, khấu hao và phân bổ
print(term.domain)   # accounting

# Works with Vietnamese abbreviations and alternate forms
lookup("TSCĐ").en          # "Fixed assets"
lookup("Tài sản lưu động") # resolves via alt_vi → Current assets
lookup("nợ xấu").en_abbr   # "NPL"

# ── Translate ───────────────────────────────────────────────────────────────
translate("Tài sản cố định", to="en")   # "Fixed assets"
translate("Revenue", to="vi")            # "Doanh thu"
translate("TNDN", to="en")             # "Corporate income tax"
translate("nonexistent", to="en")       # None

# ── Search (partial match) ───────────────────────────────────────────────────
results = search("thuế")                          # all terms containing "thuế"
results = search("income", domains=["tax"])        # domain-filtered
results = search("lợi nhuận", domains=["accounting", "banking"])

# ── Browse by domain ─────────────────────────────────────────────────────────
accounting_terms = by_domain("accounting")        # list[Term]
tax_terms        = by_domain("tax")

# ── Bulk export ──────────────────────────────────────────────────────────────
csv_str  = export("csv",      source="vi", target="en")
json_str = export("json",     source="vi", target="en", domains=["banking"])
md_str   = export("markdown", source="vi", target="en", domains=["tax"])
```

---

## Full API reference

### `lookup(term: str) -> Term | None`

Case-insensitive lookup across all surface forms: canonical EN, canonical VI, EN abbreviation, VI abbreviation, and all `alt_en` / `alt_vi` entries.

```python
lookup("Revenue")               # by canonical EN
lookup("doanh thu")             # by canonical VI (case-insensitive)
lookup("EBITDA")                # by abbreviation
lookup("TSCĐ")                  # by VI abbreviation
lookup("Tài sản dài hạn hữu hình")  # by alt_vi
lookup("  Revenue  ")           # whitespace stripped
lookup("")                      # returns None
lookup("nonexistent")           # returns None
```

### `translate(term: str, to: Literal["en", "vi"]) -> str | None`

Translate any surface form to its canonical English or Vietnamese form.

```python
translate("Doanh thu", to="en")    # "Revenue"
translate("Revenue", to="vi")      # "Doanh thu"
translate("TNDN", to="en")        # "Corporate income tax"
translate("nope", to="en")         # None
translate("x", to="fr")            # raises ValueError
```

### `search(query: str, *, domains: list[str] | None = None) -> list[Term]`

Substring search across all surface forms, definitions, and notes fields.

```python
search("thuế")                         # all terms with "thuế" anywhere
search("income", domains=["tax"])      # narrow to one domain
search("")                             # returns []
```

### `by_domain(domain: str) -> list[Term]`

Return all terms for a domain (case-insensitive).

```python
by_domain("accounting")   # 55 terms
by_domain("BANKING")      # same as by_domain("banking")
by_domain("invalid")      # []
```

### `all_terms() -> list[Term]`

Return a copy of every loaded term (230+). Mutating the list does not affect internal state.

### `export(fmt, *, source, target, domains) -> str`

Dump the glossary (or a subset) to a string.

```python
export("csv",      source="vi", target="en")
export("json",     source="en", target="vi", domains=["tax", "accounting"])
export("markdown", source="vi", target="en", domains=["banking"])
```

### `Term` dataclass

```python
@dataclass(frozen=True)
class Term:
    en:            str               # canonical English term
    vi:            str               # canonical Vietnamese term
    domain:        str               # one of 8 allowed domains
    en_abbr:       str | None        # English abbreviation (e.g. "EBITDA")
    vi_abbr:       str | None        # Vietnamese abbreviation (e.g. "TNDN")
    alt_en:        tuple[str, ...]   # alternate English surface forms
    alt_vi:        tuple[str, ...]   # alternate Vietnamese surface forms
    vas_ref:       str | None        # VAS reference (e.g. "VAS 14")
    ifrs_ref:      str | None        # IFRS/IAS reference (e.g. "IFRS 15")
    definition_en: str | None        # plain-English definition
    definition_vi: str | None        # Vietnamese definition
    notes:         str | None        # translation guidance, register caveats

    # Convenience properties
    all_en_forms:  tuple[str, ...]   # en + en_abbr + alt_en
    all_vi_forms:  tuple[str, ...]   # vi + vi_abbr + alt_vi

    def to_dict(self) -> dict[str, Any]: ...  # None/empty fields omitted
```

---

## AI translation workflow

The flagship use case: translate a Vietnamese financial book, report, or contract into English with an LLM — with **zero terminology drift** across chapters.

### 1. Generate a system prompt

```python
from vn_financial_terms import TerminologyGuide

guide = TerminologyGuide(domains=["accounting", "tax", "banking"])
system_prompt = guide.build_system_prompt(source="vi", target="en")
```

The prompt includes:
- A mandatory glossary table (Vietnamese → English)
- An abbreviation-mapping table (TNDN → CIT, TSCĐ → Fixed assets, …)
- Seven translation rules covering institutions, VAS references, register, formatting, and untranslatable terms

### 2. Pass to your LLM

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=8096,
    system=system_prompt,          # <── glossary-anchored system prompt
    messages=[{"role": "user", "content": chapter_text}],
)
print(response.content[0].text)
```

Works with any OpenAI-compatible API too:

```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": chapter_text},
    ],
)
```

### 3. Filter by chapter domain

```python
# Full book — all 230+ terms
full_guide = TerminologyGuide()

# Chapter 3 covers accounting and tax only
chapter_guide = TerminologyGuide(domains=["accounting", "tax"])

# Real-estate chapter
re_guide = TerminologyGuide(domains=["real_estate", "regulatory"])

# Or filter an existing guide
banking_guide = full_guide.filter(["banking"])
```

### 4. Export for external CAT tools

```python
guide = TerminologyGuide(domains=["banking"])

# SDL Trados / memoQ / OmegaT
guide.to_csv(source="vi", target="en")

# JSON for vector databases / custom pipelines
guide.to_json(source="vi", target="en")

# Markdown table for Notion docs or inline prompt injection
guide.to_markdown(source="vi", target="en")
```

### 5. Inject glossary mid-conversation

When your API does not support system messages:

```python
block = guide.build_glossary_block(source="vi", target="en", fmt="markdown")
user_message = f"""Translate the following using this glossary:

{block}

---

{chapter_text}
"""
```

---

## Data format

Glossary data lives in `src/vn_financial_terms/data/` as domain-split YAML files.

```yaml
- en: Fixed assets
  vi: Tài sản cố định
  vi_abbr: TSCĐ
  alt_vi:
    - Tài sản dài hạn hữu hình
  domain: accounting
  vas_ref: VAS 03
  ifrs_ref: IAS 16
  definition_en: Tangible assets held for use in production or supply of goods/services.
  notes: >
    VAS uses "Tài sản cố định hữu hình"; IFRS uses "Property, plant and equipment".
    Prefer "Tài sản cố định" in VAS-based financial statement contexts.
```

| Field | Required | Description |
| --- | --- | --- |
| `en` | ✅ | Canonical English term |
| `vi` | ✅ | Canonical Vietnamese term |
| `domain` | ✅ | One of: `accounting` `tax` `banking` `markets` `regulatory` `real_estate` `insurance` `macro` |
| `en_abbr` | — | English abbreviation |
| `vi_abbr` | — | Vietnamese abbreviation (use correct Unicode diacritics: `TSCĐ` not `TSCD`) |
| `alt_vi` | — | YAML list of alternate Vietnamese surface forms — all indexed for lookup |
| `alt_en` | — | YAML list of alternate English surface forms |
| `vas_ref` | — | VAS reference e.g. `VAS 14` |
| `ifrs_ref` | — | IFRS/IAS reference e.g. `IFRS 15` |
| `definition_en` | — | Plain-English definition |
| `definition_vi` | — | Vietnamese definition |
| `notes` | — | Translation guidance, register caveats, disambiguation hints |

---

## Adding terms

1. Fork the repo and create a branch: `git checkout -b data/add-derivatives-terms`
2. Edit the relevant YAML file in `src/vn_financial_terms/data/`
3. Run `make test` — all existing tests must pass
4. Open a pull request

Please ensure Vietnamese text uses correct Unicode diacritics, and that `notes` captures any disambiguation or VAS-vs-IFRS differences.

---

## Development

```bash
git clone https://github.com/DataCore-VietNam/vn-financial-terms
cd vn-financial-terms
make dev        # pip install -e ".[dev]" + pre-commit hooks
make test       # pytest with coverage (62 tests)
make check      # ruff lint + format check + mypy strict
make all        # check + test + build wheel
```

**Requirements:** Python 3.10+, pip. Optional: [uv](https://docs.astral.sh/uv/) for faster installs.

**CI matrix:** Python 3.10, 3.11, 3.12, 3.13 on ubuntu-latest.

---

## License

MIT (code) · CC-BY 4.0 (glossary data in `src/vn_financial_terms/data/`)
