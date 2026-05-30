# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-30

### Added
- `TerminologyGuide` class for AI-assisted translation consistency
- `build_translation_prompt()` convenience wrapper
- `search()` function for partial-match lookup across all surface forms
- `export()` function supporting CSV, JSON, and Markdown output
- `Term.alt_vi` and `Term.alt_en` fields for alternate surface forms (indexed)
- `Term.notes` field for translation guidance
- `Term.all_vi_forms` and `Term.all_en_forms` properties
- `py.typed` marker (PEP 561 -- typed package)
- Python 3.13 support
- mypy strict type-checking in CI
- YAML lint in CI
- Publish-to-PyPI workflow on version tags
- 230+ terms across all 8 domains (up from ~10)
- `examples/ai_translation.py` demonstrating the full translation workflow

### Changed
- YAML data moved to `src/vn_financial_terms/data/` (single authoritative location)
- `Term.domain` validation now references `ALLOWED_DOMAINS` module constant
- Enhanced `_build_index` to index `alt_vi` and `alt_en` forms
- `pyproject.toml` updated to v0.2.0, added `pytest-cov`, `mypy`, `types-PyYAML`

### Fixed
- `vi_abbr` for "Fixed assets" corrected to `TSCĐ` (was `TSCD`)

## [0.1.0] - 2026-05-29

### Added
- Initial release
- `lookup()`, `translate()`, `all_terms()`, `by_domain()` API
- `Term` dataclass with `en`, `vi`, `domain`, `en_abbr`, `vi_abbr`, `vas_ref`, `ifrs_ref`
- Accounting domain YAML with ~10 terms
- Hatchling build system, ruff, pre-commit

[Unreleased]: https://github.com/DataCore-VietNam/vn-financial-terms/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/DataCore-VietNam/vn-financial-terms/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DataCore-VietNam/vn-financial-terms/releases/tag/v0.1.0
