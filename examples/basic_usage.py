"""Basic usage examples for vn-financial-terms."""

from vn_financial_terms import all_terms, by_domain, lookup, search, translate

# ── Lookup by any surface form ──────────────────────────────────────────────
term = lookup("EBITDA")
assert term is not None
print(term.en)   # Earnings before interest, taxes, depreciation, and amortization
print(term.vi)   # Lợi nhuận trước lãi vay, thuế, khấu hao và phân bổ
print(term.domain)  # accounting

# Works with Vietnamese abbreviations too
fixed = lookup("TSCĐ")
assert fixed is not None
print(fixed.en, fixed.vas_ref)  # Fixed assets  VAS 03

# ── Translate ───────────────────────────────────────────────────────────────
print(translate("Tài sản cố định", to="en"))  # Fixed assets
print(translate("Revenue", to="vi"))           # Doanh thu
print(translate("TNDN", to="en"))             # Corporate income tax

# ── Search ──────────────────────────────────────────────────────────────────
tax_results = search("thuế", domains=["tax"])
print(f"Found {len(tax_results)} tax terms containing 'thuế'")

income_results = search("income")
for t in income_results[:3]:
    print(f"  {t.vi} -> {t.en}")

# ── Browse by domain ────────────────────────────────────────────────────────
banking = by_domain("banking")
print(f"\n{len(banking)} banking terms loaded")
for t in banking[:5]:
    abbr = f" ({t.en_abbr})" if t.en_abbr else ""
    print(f"  {t.vi} -> {t.en}{abbr}")

# ── Statistics ──────────────────────────────────────────────────────────────
terms = all_terms()
domains = {}
for t in terms:
    domains[t.domain] = domains.get(t.domain, 0) + 1
print("\nTerms per domain:")
for domain, count in sorted(domains.items()):
    print(f"  {domain:15s} {count:3d}")
