# Contributing

All contributions -- bug reports, new terms, definitions, translation notes -- are welcome.

## Adding or editing terms

1. Fork the repo and create a feature branch: `git checkout -b feat/add-derivatives-terms`
2. Edit the relevant YAML file in `src/vn_financial_terms/data/`
3. Run `make test` to ensure nothing breaks
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
5. Open a pull request

### YAML entry format

```yaml
- en: Revenue
  vi: Doanh thu
  domain: accounting          # one of the 8 allowed domains
  en_abbr: null               # optional English abbreviation
  vi_abbr: null               # optional Vietnamese abbreviation
  alt_vi:                     # optional alternative Vietnamese forms (list)
    - Doanh thu bán hàng
  vas_ref: VAS 14             # optional VAS reference
  ifrs_ref: IFRS 15           # optional IFRS/IAS reference
  definition_en: >            # optional plain-English definition
    Income arising in the ordinary course of business.
  definition_vi: null         # optional Vietnamese definition
  notes: >                    # optional translation guidance
    Preferred over "thu nhập" in revenue recognition contexts.
```

**Allowed domains:** `accounting`, `tax`, `banking`, `markets`,
`regulatory`, `real_estate`, `insurance`, `macro`

### Style rules

- Vietnamese text must use correct Unicode diacritics (not ASCII transliteration).
- `en` is the canonical English form; `vi` is the canonical Vietnamese form.
- `vi_abbr` should match official Vietnamese regulatory usage (e.g. `TNDN`, `TSCĐ`).
- `notes` should capture disambiguation, register guidance, or VAS-vs-IFRS differences.
- Keep each YAML entry alphabetically ordered within its file.

## Commit format

```
feat: add VN30 sector mapping
fix: correct TSCĐ abbreviation diacritic
data: add 10 new insurance terms
docs: clarify transfer-pricing note
test: add coverage for alt_vi lookup
```

## Running locally

```bash
pip install -e ".[dev]"
make test       # run tests
make check      # lint + type-check
```

## License

By contributing you agree your contributions are licensed under MIT (code)
and CC-BY 4.0 (glossary data).
