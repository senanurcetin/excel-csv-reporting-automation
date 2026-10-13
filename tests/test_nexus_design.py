"""Offline source contracts for reproducible NEXUS reporting artifacts."""
import unittest
from pathlib import Path

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
            self.assertIn("Revenue policy & controls", html)
            self.assertIn("prefers-reduced-motion", html)
        self.assertIn("NEXUS / SALES DATA INTELLIGENCE", source)
        self.assertIn("prefers-reduced-motion", source)


if __name__ == "__main__":
    unittest.main()
