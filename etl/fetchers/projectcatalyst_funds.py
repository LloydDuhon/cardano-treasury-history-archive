"""projectcatalyst.io fund pages and IOG voting-results PDF fetcher.

Source:        https://projectcatalyst.io/funds/{N} and the votingResultsUrl
               embedded in each page's Next.js JSON.
Coverage:      Funds 2-13 PDFs (canonical winner artifacts);
               F10-F15 also link inline voting-results pages.

Phase 2 work:
  1. Fetch each /funds/{N} HTML; parse the embedded __NEXT_DATA__ JSON.
  2. Extract canonical counts (proposals / funded / completed) and
     votingResultsUrl per fund.
  3. Download each linked PDF (handle Google Drive redirects) into
     ../data/funds/fund-XX/_provenance/iohk-pdfs/.
  4. Parse PDFs with pdfplumber to extract proposal title + funded flag +
     ask amount; emit a structured intermediate file under
     ../data/funds/fund-XX/_intermediate/iohk_winners.json.

Status: NOT IMPLEMENTED (Phase 2). This module is a typed stub.
"""

from __future__ import annotations

from pathlib import Path


def fetch_fund_landing_pages(*, output_root: Path) -> None:
    """Fetch the projectcatalyst.io HTML for each fund and extract Next.js JSON."""
    raise NotImplementedError("Phase 2.")


def download_voting_results_pdfs(*, output_root: Path) -> None:
    """Download the canonical IOG voting-results PDF for each fund where available."""
    raise NotImplementedError("Phase 2.")


def parse_voting_results_pdf(pdf_path: Path) -> None:
    """Parse a voting-results PDF into a structured intermediate JSON.

    Args:
        pdf_path: Filesystem path to a captured PDF.

    Raises:
        NotImplementedError: Phase 2 implementation pending.
    """
    raise NotImplementedError("Phase 2.")
