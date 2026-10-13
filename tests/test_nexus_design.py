"""Offline source contracts for reproducible NEXUS reporting artifacts."""
import unittest
import json
from pathlib import Path
from reporting import build_html

ROOT = Path(__file__).resolve().parents[1]


class NexusReportingDesignTests(unittest.TestCase):
    def test_generated_and_published_report_have_matching_nexus_brand(self):
        source = (ROOT / "reporting.py").read_text(encoding="utf-8")
        for name in ("outputs/index.html", "outputs/dashboard.html"):
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("NEXUS / SALES DATA INTELLIGENCE", html)
            self.assertIn("#071829", html)
            self.assertIn("#4ea8ff", html)
            self.assertIn("SYNTHETIC DATA ONLY", html)
            self.assertIn('class="nexus-sales-brand"', html)
            self.assertIn('class="nexus-sales-mark"', html)
            self.assertIn("DATA INTELLIGENCE / CLIENT REPORTING", html)
            self.assertIn("Revenue policy & controls", html)
            self.assertIn("prefers-reduced-motion", html)
        for source_or_html in (source,
                               (ROOT / "outputs/index.html").read_text(encoding="utf-8"),
                               (ROOT / "outputs/dashboard.html").read_text(encoding="utf-8")):
            self.assertIn('class="barlabel" title=', source_or_html)
            self.assertIn('aria-hidden="true"', source_or_html)
            self.assertIn("max-width:460px", source_or_html)
        self.assertIn('class="nexus-sales-brand"', source)
        self.assertIn("SYNTHETIC SALES REPORT", source)
        self.assertIn("prefers-reduced-motion", source)

    def test_mutual_reconciliation_semantics_always_match_data(self):
        summary = json.loads((ROOT / "outputs/validation_summary.json").read_text(encoding="utf-8"))
        passing = build_html(summary)
        self.assertIn('class="card reconciliation-pass"', passing)
        self.assertIn('>PASS</strong>', passing)
        failing = build_html({**summary, "reconciliation_passed": False})
        self.assertIn('class="card reconciliation-fail"', failing)
        self.assertIn('>FAIL</strong>', failing)
        self.assertNotIn('class="card reconciliation-pass"', failing)


if __name__ == "__main__":
    unittest.main()
