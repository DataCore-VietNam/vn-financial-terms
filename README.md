# vn-financial-terms

Bilingual (Vietnamese <-> English) glossary of financial, accounting, tax, banking, and regulatory terminology used in Vietnam. Designed for both programmatic lookup and AI-assisted translation workflows.

[![CI](https://github.com/DataCore-VietNam/vn-financial-terms/actions/workflows/ci.yml/badge.svg)](https://github.com/DataCore-VietNam/vn-financial-terms/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vn-financial-terms)](https://pypi.org/project/vn-financial-terms/)
[![Python](https://img.shields.io/pypi/pyversions/vn-financial-terms)](https://pypi.org/project/vn-financial-terms/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Coverage

230+ terms across 8 domains:

- **Accounting** -- VAS / IFRS cross-references, financial statements, ratios
- **Tax** -- CIT (TNDN), PIT (TNCN), VAT (GTGT), transfer pricing, tax administration
- **Banking** -- SBV regulations, NPL, CAR, NIM, AML/KYC, Basel
- **Markets** -- HOSE, HNX, UPCoM, derivatives, foreign ownership limits
- **Regulatory** -- SSC, MOF, legal instruments (Thong tu, Nghi dinh), VAS/VSA
- **Real estate** -- Land use rights, GCNQSD, FAR, industrial zones
- **Insurance** -- Life / non-life, reinsurance, solvency, actuarial
- **Macro** -- GDP, CPI, FDI, monetary policy, exchange rates

## Install

```bash
pip install vn-financial-terms
```

## Quick start

```python
from vn_financial_terms import lookup, translate, search

# Lookup by any surface form -- EN, VI, abbreviation, or alternate spelling
lookup("EBITDA")
# Term(en='Earnings before interest, taxes, depreciation, and amortization',
#      vi='Loi nhuan truoc lai vay, thue, khau hao va phan bo',
#      en_abbr='EBITDA', vi_abbr='EBITDA', domain='accounting', ...)

translate("Tai san co dinh", to="en")   # "Fixed assets"
translate("Revenue", to="vi")            # "Doanh thu"
translate("TSCĐ", to="en")             # "Fixed assets"

# Partial-match search
results = search("khau hao", domains=["accounting"])
```

## AI translation

The flagship use case: pin every term to its canonical translation before
sending text to an LLM, so the model never drifts between chapters or
documents.

```python
from vn_financial_terms import TerminologyGuide

# Build a system prompt for a Vietnamese -> English book translation
guide = TerminologyGuide(domains=["accounting", "tax", "banking"])
system_prompt = guide.build_system_prompt(source="vi", target="en")

# Pass to your preferred LLM
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": chapter_text}],
)
```

The generated system prompt includes a mandatory glossary table, an
abbreviation-mapping table, and seven translation rules covering
institutions, VAS references, register, and formatting.

### Export formats

For external CAT tools or custom pipelines:

```python
guide = TerminologyGuide(domains=["banking"])

guide.to_csv()       # SDL Trados, memoQ, OmegaT
guide.to_json()      # custom pipelines, vector databases
guide.to_markdown()  # embed in prompts or Notion docs

# Or inject as a glossary block in the user message
block = guide.build_glossary_block(fmt="markdown")
```

### Filter by chapter domain

```python
full_guide  = TerminologyGuide()                         # all 230+ terms
re_guide    = full_guide.filter(["real_estate"])          # narrow to one domain
combo_guide = TerminologyGuide(domains=["regulatory", "markets"])
```

### Convenience wrapper

```python
from vn_financial_terms import build_translation_prompt

prompt = build_translation_prompt(source="vi", target="en",
                                  domains=["accounting"])
```

## Data

Glossary data lives in `src/vn_financial_terms/data/` as domain-split YAML
files. Each entry supports:

| Field | Type | Description |
| --- | --- | --- |
| `en` | str | Canonical English term (required) |
| `vi` | str | Canonical Vietnamese term (required) |
| `domain` | str | One of the 8 domains (required) |
| `en_abbr` | str | English abbreviation (e.g. EBITDA) |
| `vi_abbr` | str | Vietnamese abbreviation (e.g. TNDN) |
| `alt_vi` | list | Alternative Vietnamese forms (indexed for lookup) |
| `alt_en` | list | Alternative English forms |
| `vas_ref` | str | VAS reference (e.g. VAS 14) |
| `ifrs_ref` | str | IFRS/IAS reference (e.g. IFRS 15) |
| `definition_en` | str | Plain-English definition |
| `definition_vi` | str | Vietnamese definition |
| `notes` | str | Translation guidance, register caveats, disambiguation |

To add terms, edit the relevant YAML file and open a PR.

## API reference

```python
from vn_financial_terms import (
    lookup,              # exact + alternate-form lookup -> Term | None
    translate,           # surface form -> str | None
    search,              # partial-match -> list[Term]
    all_terms,           # all loaded terms -> list[Term]
    by_domain,           # filter by domain -> list[Term]
    export,              # dump to CSV / JSON / Markdown -> str
    TerminologyGuide,    # AI translation helper class
    build_translation_prompt,  # convenience wrapper
    Term,                # dataclass for a single entry
)
```

## Development

```bash
git clone https://github.com/DataCore-VietNam/vn-financial-terms
cd vn-financial-terms
make dev        # installs package + dev deps + pre-commit hooks
make test       # pytest with coverage
make check      # lint + format-check + mypy
make all        # check + test + build
```

Requirements: Python 3.10+, pip, (optional) [uv](https://docs.astral.sh/uv/).

## License

MIT (code) + CC-BY 4.0 (glossary data in `src/vn_financial_terms/data/`)
