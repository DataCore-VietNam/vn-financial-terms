"""vn-financial-terms -- Bilingual Vietnamese <-> English financial glossary.

Covers Vietnamese Accounting Standards (VAS), IFRS cross-references,
tax codes, SBV banking terminology, HOSE/HNX market vocabulary,
securities regulation, real-estate, insurance, and macro terms.

Basic usage
-----------
>>> from vn_financial_terms import lookup, translate
>>> lookup("EBITDA").vi
'Lợi nhuận trước lãi vay, thuế, khấu hao và phân bổ'
>>> translate("Tài sản cố định", to="en")
'Fixed assets'

AI translation
--------------
>>> from vn_financial_terms import TerminologyGuide
>>> guide = TerminologyGuide(domains=["accounting", "tax"])
>>> prompt = guide.build_system_prompt(source="vi", target="en")
"""

from vn_financial_terms.glossary import (
    all_terms,
    by_domain,
    export,
    lookup,
    search,
    translate,
)
from vn_financial_terms.models import Term
from vn_financial_terms.translation import TerminologyGuide, build_translation_prompt

__version__ = "0.2.0"

__all__ = [
    # Core model
    "Term",
    # AI translation
    "TerminologyGuide",
    # Package metadata
    "__version__",
    "all_terms",
    "build_translation_prompt",
    "by_domain",
    # Export
    "export",
    # Lookup / query
    "lookup",
    "search",
    "translate",
]
