"""Real-browser acceptance for the self-contained, generated NEXUS report.

Run locally (no hosted CI):
    python -m unittest discover -s tests -p 'test_visual_acceptance.py' -v

If Playwright or its Chromium binary is not installed the suite is skipped.
To capture *actual* screenshots, set E2E_SCREENSHOT_DIR to a local folder.
"""
from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "index.html"


class NexusReportBrowserAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise unittest.SkipTest("Install playwright before browser acceptance") from error
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception as error:
            cls.playwright.stop()
            raise unittest.SkipTest("Playwright Chromium browser not installed") from error

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def open_report(self, width: int, height: int):
        page = self.browser.new_page(viewport={"width": width, "height": height})
        self.addCleanup(page.close)
        page.goto(REPORT.as_uri(), wait_until="load")
        return page

    @staticmethod
    def screenshot_if_requested(page, name):
        output = os.environ.get("E2E_SCREENSHOT_DIR")
        if output:
            directory = Path(output)
            directory.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(directory / name), full_page=True)

    def test_premium_desktop_layout_and_real_brand_provenance(self):
        page = self.open_report(1440, 900)
        self.assertTrue(page.get_by_role("heading", name="From inconsistent files to trusted KPIs").is_visible())
        self.assertTrue(page.get_by_text("SYNTHETIC DATA ONLY", exact=True).is_visible())
        self.assertTrue(page.locator(".nexus-sales-brand").is_visible())
        self.assertEqual(page.locator(".card").count(), 4)
        self.assertGreater(page.locator(".barrow").count(), 0)
        self.assertEqual(page.locator(".card.reconciliation-pass,.card.reconciliation-fail").count(), 1)
        self.screenshot_if_requested(page, "nexus-sales-desktop-1440.png")

    def test_mobile_375_has_no_document_horizontal_overflow(self):
        page = self.open_report(375, 812)
        geometry = page.evaluate("""() => ({
            scroll: document.documentElement.scrollWidth,
            viewport: document.documentElement.clientWidth
        })""")
        self.assertLessEqual(geometry["scroll"], geometry["viewport"] + 1, geometry)
        self.assertTrue(page.locator(".nexus-sales-brand").is_visible())
        self.assertTrue(page.locator(".grid .card").first.is_visible())
        page.locator(".sections .panel").last.scroll_into_view_if_needed()
        self.assertTrue(page.locator(".sections .panel").last.is_visible())
        self.screenshot_if_requested(page, "nexus-sales-mobile-375.png")

    def test_print_ink_and_chart_labels_remain_readable(self):
        page = self.open_report(1440, 900)
        page.emulate_media(media="print")
        ink = page.locator(".card strong").first.evaluate("el => getComputedStyle(el).color")
        label = page.locator(".barlabel").first.evaluate("el => getComputedStyle(el).color")
        paper = page.locator("body").evaluate("el => getComputedStyle(el).backgroundColor")
        self.assertEqual(ink, "rgb(19, 44, 68)")
        self.assertEqual(label, "rgb(19, 44, 68)")
        self.assertEqual(paper, "rgb(255, 255, 255)")
        self.screenshot_if_requested(page, "nexus-sales-print-preview.png")


if __name__ == "__main__":
    unittest.main()
